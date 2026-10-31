from Constants import OPENROUTER_MODEL, OPENROUTER_API_KEY, LLM_PROVIDER
from EnvHelper import set_env_variable

def saveOpenRouterSettings(model: str, api_key: str) -> None:
    set_env_variable(OPENROUTER_MODEL, model)
    set_env_variable(OPENROUTER_API_KEY, api_key)

def setLLMProvider(provider: str) -> None:
    set_env_variable(LLM_PROVIDER, provider)
