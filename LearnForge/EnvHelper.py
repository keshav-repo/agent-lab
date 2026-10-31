from pathlib import Path

from dotenv import set_key, get_key

DEFAULT_ENV_FILE = Path(__file__).resolve().parent / ".env"

def set_env_variable(key: str, value: str, env_file: str | Path = DEFAULT_ENV_FILE) -> None:
    set_key(str(env_file), key, value)

def get_env_variable(key: str, env_file: str | Path = DEFAULT_ENV_FILE) -> str | None:
    return get_key(str(env_file), key)
