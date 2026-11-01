# use Excalidraw MCP


import asyncio
import json
import os
import shlex
import shutil
import urllib.request
import webbrowser
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents.mcp import MCPServerStdio
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)

from logger import L

set_tracing_disabled(True)

load_dotenv(Path(__file__).resolve().parent / ".env")

MODEL_NAME = os.getenv("OPENROUTER_MODEL", "gpt-luna")
PROJECT_DIR = Path(__file__).resolve().parent
CANVAS_URL = os.getenv("EXPRESS_SERVER_URL", "http://127.0.0.1:3000")
EXPORT_DIR = Path(
    os.getenv("EXCALIDRAW_EXPORT_DIR", str(PROJECT_DIR / "diagram_exports"))
).expanduser().resolve()


def _mcp_command() -> tuple[str, list[str], dict[str, str]]:
    """Resolve the Excalidraw MCP command, allowing local/custom server installs."""
    command = os.getenv("EXCALIDRAW_MCP_COMMAND", "npx")
    args = shlex.split(os.getenv("EXCALIDRAW_MCP_ARGS", "-y mcp-excalidraw-server"))
    executable = shutil.which(command)
    if executable is None and command == "npx":
        nvm_versions = Path.home() / ".nvm" / "versions" / "node"
        if nvm_versions.is_dir():
            candidates = []
            for version_dir in nvm_versions.iterdir():
                try:
                    major = int(version_dir.name.lstrip("v").split(".")[0])
                except ValueError:
                    continue
                npx = version_dir / "bin" / "npx"
                if major >= 20 and npx.exists():
                    candidates.append((major, npx))
            if candidates:
                executable = str(max(candidates)[1])
    if executable is None:
        raise RuntimeError(
            f"Could not find '{command}'. Install Node.js 20+ (including npx), "
            "or set EXCALIDRAW_MCP_COMMAND to the MCP server executable."
        )

    env = dict(os.environ)
    env.update({
        "EXPRESS_SERVER_URL": CANVAS_URL,
        "ENABLE_CANVAS_SYNC": os.getenv("ENABLE_CANVAS_SYNC", "true"),
        "EXCALIDRAW_EXPORT_DIR": str(EXPORT_DIR),
    })
    executable_dir = str(Path(executable).parent)
    env["PATH"] = executable_dir + os.pathsep + env.get("PATH", "")
    return executable, args, env

@lru_cache(maxsize=1)
def _openrouter_model_pricing() -> tuple[float, float] | None:
    """Return OpenRouter's per-token input/output prices for the configured model."""
    try:
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={"User-Agent": "LearnForge"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            models = json.load(response).get("data", [])
        model = next((item for item in models if item.get("id") == MODEL_NAME), None)
        if model is None:
            L.warning("OpenRouter pricing not found for model %s", MODEL_NAME)
            return None
        pricing = model.get("pricing", {})
        return float(pricing["prompt"]), float(pricing["completion"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        L.warning("Could not retrieve OpenRouter pricing for %s: %s", MODEL_NAME, e)
        return None


def _estimate_usage_cost(input_tokens: int, output_tokens: int) -> float | None:
    """Estimate USD cost; optional overrides are expressed per million tokens."""
    pricing = _openrouter_model_pricing()
    input_rate, output_rate = pricing if pricing is not None else (None, None)
    for env_name, current, is_input in (
        ("OPENROUTER_INPUT_PRICE_PER_MILLION", input_rate, True),
        ("OPENROUTER_OUTPUT_PRICE_PER_MILLION", output_rate, False),
    ):
        value = os.getenv(env_name)
        if value:
            try:
                rate = float(value) / 1_000_000
            except ValueError:
                L.warning("Ignoring invalid %s value: %s", env_name, value)
                continue
            if is_input:
                input_rate = rate
            else:
                output_rate = rate
    if input_rate is None or output_rate is None:
        return None
    return input_tokens * input_rate + output_tokens * output_rate


def _log_usage(result) -> None:
    usage = result.context_wrapper.usage
    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens
    cost = _estimate_usage_cost(input_tokens, output_tokens)
    if cost is None:
        L.info(
            "DrawIoAgent usage | model=%s | input_tokens=%s | output_tokens=%s "
            "| cost_estimate=unavailable (set OpenRouter price overrides if needed)",
            MODEL_NAME, input_tokens, output_tokens,
        )
        return
    L.info(
        "DrawIoAgent usage | model=%s | input_tokens=%s | output_tokens=%s "
        "| estimated_cost=$%.8f (%.6f cents)",
        MODEL_NAME, input_tokens, output_tokens, cost, cost * 100,
    )


AGENT_INSTRUCTIONS = """
You are LearnForge's Excalidraw diagramming assistant. Use the connected Excalidraw
MCP tools to create and modify the user's live diagram; do not merely describe a
diagram in text. Keep the same canvas across turns so follow-up requests refine the
existing work.

For a new diagram, first inspect the current canvas. If it contains a diagram, ask
before replacing it. For each request, understand the audience and purpose, plan a
clear high-level structure, then create the diagram using the available MCP tools.
Prefer a small number of meaningful groups, concise labels, consistent colors,
generous spacing, a clear reading direction, and arrows that communicate the flow.
Avoid unnecessary implementation detail and visual clutter. After drawing or
editing, inspect the canvas with the available describe/screenshot tools, fix
overlaps or unreadable labels, and make sure the result fits the viewport.

Treat later user messages as edits to the current diagram unless they explicitly
request a new one. Before deleting/replacing user work, ask for confirmation. When
asked to save/export, use the MCP export tool and a path under the configured export
directory unless the user gives another path. Report the canvas URL and any exported
file path only after the corresponding action succeeds. Be concise and state clearly
if an MCP operation failed; never claim an edit or export succeeded if it did not.
""".strip()


async def chat() -> None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing; add it to the .env file.")
    command, args, env = _mcp_command()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    try:
        async with MCPServerStdio(
            name="excalidraw",
            params={"command": command, "args": args, "env": env},
            client_session_timeout_seconds=120,
        ) as server:
            agent = Agent(
                name="LearnForgeExcalidrawAgent",
                instructions=AGENT_INSTRUCTIONS,
                mcp_servers=[server],
                model=OpenAIChatCompletionsModel(
                    model=MODEL_NAME,
                    openai_client=client,
                ),
            )
            history: list = []
            print(
                "Excalidraw assistant ready. Describe a diagram or request edits; "
                "the canvas stays active between turns. Commands: /open, /clear "
                "(chat context only), /help, /exit."
            )
            if os.getenv("EXCALIDRAW_OPEN_BROWSER", "1").lower() not in {"0", "false", "no"}:
                webbrowser.open(CANVAS_URL)
            print(f"Live canvas: {CANVAS_URL}\nExports: {EXPORT_DIR}")

            while True:
                try:
                    prompt = (await asyncio.to_thread(input, "\nDiagram> ")).strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not prompt:
                    continue
                command_text = prompt.lower()
                if command_text in {"/exit", "/quit", "exit", "quit", "q"}:
                    break
                if command_text == "/help":
                    print(
                        "Describe a new high-level diagram, then ask for changes in "
                        "natural language. /open opens the live canvas; /clear resets "
                        "chat context only; /exit quits. Ask the agent to export/save "
                        "to create an .excalidraw file."
                    )
                    continue
                if command_text == "/open":
                    webbrowser.open(CANVAS_URL)
                    print(f"Opened {CANVAS_URL}")
                    continue
                if command_text == "/clear":
                    history = []
                    print("Chat context cleared; the live canvas was not changed.")
                    continue

                try:
                    result = await Runner.run(
                        agent,
                        history + [{"role": "user", "content": prompt}],
                        max_turns=60,
                    )
                    history = result.to_input_list()
                    _log_usage(result)
                    print(f"\n{result.final_output}")
                except Exception as e:  # Keep the interactive session alive on errors.
                    L.exception("Excalidraw agent turn failed")
                    print(f"Could not complete that request: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(chat())
    except (RuntimeError, OSError) as e:
        L.error("Could not start Excalidraw assistant: %s", e)
        raise SystemExit(1) from e

