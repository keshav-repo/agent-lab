from dotenv import set_key, get_key

def set_env_variable(key: str, value: str, env_file: str = ".env") -> None:
    set_key(env_file, key, value)

def get_env_variable(key: str, env_file: str = ".env") -> str | None:
    return get_key(env_file, key)
