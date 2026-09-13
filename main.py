import asyncio
import sys
from pathlib import Path


USERBOT_DIR = Path(__file__).resolve().parent / "userbot"
sys.path.insert(0, str(USERBOT_DIR))

from main import main as run_userbot  # noqa: E402


if __name__ == "__main__":
    asyncio.run(run_userbot())
