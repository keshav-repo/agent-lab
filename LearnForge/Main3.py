import asyncio
from browser_use import Agent, BrowserProfile, BrowserSession, ChatOpenAI

from Main2 import (
    Instagram_link,
    MODEL_NAME,
    PROFILE_NAME,
    _prepare_profile_copy,
    api_key,
)

CHROME_EXECUTABLE = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

async def main() -> None:
    # Chrome can't be automated on its default (possibly open) data dir, so use the
    # lightweight copy of PROFILE_NAME (cookies/storage) prepared by Main2.
    profile = BrowserProfile(
        executable_path=CHROME_EXECUTABLE,
        user_data_dir=_prepare_profile_copy(),
        profile_directory=PROFILE_NAME,
        headless=False,
        keep_alive=False,
    )
    browser = BrowserSession(browser_profile=profile)

    # OpenRouter via the OpenAI-compatible API (browser_use's own OpenAI client).
    model = ChatOpenAI(
        model=MODEL_NAME,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    agent = Agent(
        task=(
            f"Open {Instagram_link}, and return the post's author username and full "
            "caption text. If a login wall appears, say so."
        ),
        llm=model,
        browser_session=browser,
    )

    result = await agent.run()
    print(result.final_result())


if __name__ == "__main__":
    asyncio.run(main())
