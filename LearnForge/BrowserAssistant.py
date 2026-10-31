import asyncio
import json
import os
import shutil
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
        print("Browser assistant ready. Type a task, 'clear' to reset context, 'exit' to quit.")
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
                print("Context cleared.")
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
            print(f"\n{result.final_output}")


if __name__ == "__main__":
    asyncio.run(chat())
