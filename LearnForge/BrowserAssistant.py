import asyncio
import json
import os
import shutil
import subprocess
import urllib.request
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
from models import DuplicateCheckResult, DuplicateClassification, NearestLearningItem

set_tracing_disabled(True)

load_dotenv(Path(__file__).resolve().parent / ".env")

MODEL_NAME = os.getenv("OPENROUTER_MODEL", "gpt-luna")
api_key = os.getenv("OPENROUTER_API_KEY")
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

CHROME_USER_DIRECTORY = '/Users/keshavkumar/Library/Application Support/Google/Chrome'
Instagram_link = 'https://www.instagram.com/p/DeHh6neBo9Q/'

PROFILE_NAME = "Default"

# Playwright can't attach to a Chrome profile that is already open (and Chrome blocks
# automation on its default data dir), so a lightweight copy of the profile is used.
AUTOMATION_PROFILE_DIR = Path(__file__).resolve().parent / ".chrome_automation_profile"
_PROFILE_ITEMS = [
    "Cookies", "Cookies-journal", "Network", "Local Storage", "Session Storage",
    "IndexedDB", "Preferences", "Secure Preferences", "Web Data",
]


def _prepare_profile_copy(refresh: bool = True) -> str:
    """Copy login-related data (cookies, storage) of PROFILE_NAME into a separate dir."""
    src_root = Path(CHROME_USER_DIRECTORY)
    src = src_root / PROFILE_NAME
    dst = AUTOMATION_PROFILE_DIR / PROFILE_NAME
    if dst.exists() and not refresh:
        return str(AUTOMATION_PROFILE_DIR)
    dst.mkdir(parents=True, exist_ok=True)
    if (src_root / "Local State").exists():
        shutil.copy2(src_root / "Local State", AUTOMATION_PROFILE_DIR / "Local State")
    for name in _PROFILE_ITEMS:
        s, d = src / name, dst / name
        if not s.exists():
            continue
        try:
            if s.is_dir():
                shutil.copytree(s, d, dirs_exist_ok=True, ignore_dangling_symlinks=True)
            else:
                shutil.copy2(s, d)
        except (OSError, shutil.Error) as e:
            L.warning(f"Could not copy {name}: {e}")
    return str(AUTOMATION_PROFILE_DIR)


def _write_playwright_config() -> str:
    """Playwright MCP config: launch Chrome with the given profile."""
    config = {
        "browser": {
            "browserName": "chromium",
            "userDataDir": _prepare_profile_copy(),
            "launchOptions": {
                "channel": "chrome",
                "headless": False,
                "args": [f"--profile-directory={PROFILE_NAME}"],
                # Playwright's default mock keychain can't decrypt the copied cookies
                # (they're encrypted with the real macOS keychain), so they'd be dropped.
                "ignoreDefaultArgs": ["--use-mock-keychain", "--password-store=basic"],
            },
        }
    }
    path = Path(__file__).resolve().parent / "playwright_mcp_config.json"
    path.write_text(json.dumps(config, indent=2))
    return str(path)


def _node_bin_dir() -> str | None:
    """Find a Node >= 20 bin dir (Playwright MCP requires it); prefer nvm installs."""
    versions = Path.home() / ".nvm" / "versions" / "node"
    if versions.is_dir():
        candidates = []
        for d in versions.iterdir():
            try:
                major = int(d.name.lstrip("v").split(".")[0])
            except ValueError:
                continue
            if major >= 20 and (d / "bin" / "npx").exists():
                candidates.append((major, d / "bin"))
        if candidates:
            return str(max(candidates)[1])
    return None

AGENT_INSTRUCTIONS = (
    "You are a browser automation assistant controlling the user's Chrome (already "
    "logged in to their accounts) through Playwright browser tools. Do whatever the "
    "user asks in the browser: navigate, click, type, scroll, read and extract page "
    "content, etc. Take a snapshot to see the page before acting. Never invent page "
    "content; report only what you actually see. Be concise. Ask before irreversible "
    "actions (posting, deleting, purchasing, sending messages)."
)

def copy_to_clipboard(text: str) -> bool:
    """Copy text to the system clipboard (macOS pbcopy; falls back to xclip/clip)."""
    for cmd in (["pbcopy"], ["xclip", "-selection", "clipboard"], ["clip"]):
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, input=text.encode("utf-8"), check=True)
                return True
            except (OSError, subprocess.SubprocessError):
                return False
    return False


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
            "BrowserAssistant usage | model=%s | input_tokens=%s | output_tokens=%s "
            "| cost_estimate=unavailable (set OpenRouter price overrides if needed)",
            MODEL_NAME, input_tokens, output_tokens,
        )
        return
    L.info(
        "BrowserAssistant usage | model=%s | input_tokens=%s | output_tokens=%s "
        "| estimated_cost=$%.8f (%.6f cents)",
        MODEL_NAME, input_tokens, output_tokens, cost, cost * 100,
    )


async def chat() -> None:
    node_bin = _node_bin_dir()
    env = dict(os.environ)
    if node_bin:
        env["PATH"] = node_bin + os.pathsep + env.get("PATH", "")
    async with MCPServerStdio(
        name="playwright",
        params={
            "command": str(Path(node_bin) / "npx") if node_bin else "npx",
            "args": ["-y", "@playwright/mcp@latest", "--config", _write_playwright_config()],
            "env": env,
        },
        client_session_timeout_seconds=120,
    ) as server:
        agent = Agent(
            name="BrowserAssistant",
            instructions=AGENT_INSTRUCTIONS,
            mcp_servers=[server],
            model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
        )
        history: list = []
        last_output = ""
        print(
            "Browser assistant ready. Type a task, '/clipboard' to copy the previous "
            "response, '/save <file path>' to save it, 'clear' to reset context, "
            "'exit' to quit."
        )
        while True:
            try:
                prompt = (await asyncio.to_thread(input, "\n> ")).strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not prompt:
                continue
            if prompt.lower() in {"exit", "quit", "q"}:
                break
            if prompt.lower() == "clear":
                history = []
                last_output = ""
                print("Context cleared.")
                continue
            if prompt.lower() == "/clipboard":
                if not last_output:
                    print("Nothing to copy yet.")
                elif copy_to_clipboard(last_output):
                    print("Previous response copied to clipboard.")
                else:
                    print("Could not access the clipboard.")
                continue
            if prompt.lower().startswith("/save"):
                file_path = prompt[len("/save"):].strip().strip('"').strip("'")
                if not file_path:
                    print("Usage: /save <file path>")
                    continue
                if not last_output:
                    print("Nothing to save yet.")
                    continue
                destination = Path(file_path).expanduser()
                try:
                    if destination.exists():
                        confirm = (await asyncio.to_thread(
                            input, f"{destination} exists. Overwrite? [y/N]: "
                        )).strip().lower()
                        if confirm not in {"y", "yes"}:
                            print("Save cancelled.")
                            continue
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(last_output, encoding="utf-8")
                    print(f"Saved previous response to {destination.resolve()}")
                except OSError as e:
                    print(f"Could not save file: {e}")
                continue
            try:
                result = await Runner.run(
                    agent,
                    history + [{"role": "user", "content": prompt}],
                    max_turns=50,
                )
            except Exception as e:  # keep the session alive on errors
                print(f"Error: {e}")
                continue
            history = result.to_input_list()
            last_output = str(result.final_output)
            _log_usage(result)
            print(f"\n{last_output}")


if __name__ == "__main__":
    asyncio.run(chat())
