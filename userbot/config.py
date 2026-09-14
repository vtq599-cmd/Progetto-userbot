import os
from pathlib import Path

from dotenv import load_dotenv


# Load userbot/.env when it exists. Real environment variables take precedence.
ENV_FILE = Path(__file__).with_name(".env")
load_dotenv(ENV_FILE)


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Переменная {name} обязательна")
    return value


try:
    API_ID = int(_required("API_ID"))
except ValueError as exc:
    raise ValueError("API_ID должен быть целым числом") from exc

if API_ID <= 0:
    raise ValueError("API_ID должен быть положительным числом")

API_HASH = _required("API_HASH")

# MTProxy is required for this deployment. Do not start without all values.
PROXY_SERVER = _required("PROXY_SERVER")
try:
    PROXY_PORT = int(_required("PROXY_PORT"))
except ValueError as exc:
    raise ValueError("PROXY_PORT должен быть целым числом") from exc

if not 1 <= PROXY_PORT <= 65535:
    raise ValueError("PROXY_PORT должен быть в диапазоне 1-65535")

PROXY_SECRET = _required("PROXY_SECRET")

PROXY_PROTOCOL = os.environ.get("PROXY_PROTOCOL", "auto").strip().lower()
if PROXY_PROTOCOL not in {"auto", "intermediate", "randomized"}:
    raise ValueError(
        "PROXY_PROTOCOL должен быть auto, intermediate или randomized"
    )

if PROXY_PROTOCOL == "auto":
    is_dd_secret = (
        len(PROXY_SECRET) == 34
        and PROXY_SECRET[:2].lower() == "dd"
        and all(char in "0123456789abcdefABCDEF" for char in PROXY_SECRET)
    )
    PROXY_PROTOCOL = "randomized" if is_dd_secret else "intermediate"

# Keep the session next to this file so it is covered by userbot/.gitignore.
SESSION_NAME = os.environ.get(
    "SESSION_NAME",
    str(Path(__file__).with_name("userbot")),
).strip()
if not SESSION_NAME:
    raise ValueError("SESSION_NAME не может быть пустым")
