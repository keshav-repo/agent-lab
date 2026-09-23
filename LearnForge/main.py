from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

set_tracing_disabled(True)

MODEL_NAME = "llama3.2"

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

INSTRUCTIONS = """
you are a communication agent to heal someone
"""

sample_agent = Agent(
    name="Search Agent",
    instructions=INSTRUCTIONS,
    model=OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client,
    ),
)

if __name__ == "__main__":
    result = Runner.run_sync(sample_agent, "Hello!")
    print(result.final_output)

