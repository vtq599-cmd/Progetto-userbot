import os


API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION_NAME = os.environ.get("SESSION_NAME", "userbot")

# MTProxy is optional. Leave PROXY_SERVER empty to connect directly.
PROXY_SERVER = os.environ.get("PROXY_SERVER", "")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "0"))
PROXY_SECRET = os.environ.get("PROXY_SECRET", "")

if not API_ID or not API_HASH:
    raise ValueError("API_ID и API_HASH должны быть установлены в переменных окружения!")
