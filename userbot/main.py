import os
import sys
import glob
import importlib
import asyncio
import logging

from telethon import TelegramClient
from config import API_ID, API_HASH, SESSION_NAME

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s — %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("userbot")

PREFIX = os.environ.get("PREFIX", ".")
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


def load_modules():
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    sys.path.insert(0, os.path.dirname(__file__))

    module_files = glob.glob(os.path.join(modules_dir, "*.py"))
    loaded = 0

    for path in sorted(module_files):
        filename = os.path.basename(path)
        if filename.startswith("_"):
            continue

        module_name = f"modules.{filename[:-3]}"
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "register"):
                mod.register(client, PREFIX)
            elif hasattr(mod, "init"):
                mod.init(client)
            log.info(f"✅ Загружен модуль: {filename[:-3]}")
            loaded += 1
        except Exception as e:
            log.error(f"❌ Ошибка при загрузке {filename[:-3]}: {e}")

    log.info(f"Загружено модулей: {loaded}")


async def main():
    log.info("Запускаю юзербота...")
    load_modules()

    await client.start()

    me = await client.get_me()
    log.info(f"Авторизован как: {me.first_name} (@{me.username})")
    log.info(f"Префикс: {PREFIX}")
    log.info("Юзербот запущен и слушает события.")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
