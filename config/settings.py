import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


MONGO_URI = get_env_variable("MONGO_URI")
