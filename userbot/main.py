import asyncio
import glob
import importlib
import logging
import os
import sys

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.network.connection import ConnectionTcpMTProxyRandomizedIntermediate

from config import (
    API_HASH,
    API_ID,
    PROXY_PORT,
    PROXY_SECRET,
    PROXY_SERVER,
    SESSION_NAME,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("userbot")

PREFIX = os.environ.get("BOT_PREFIX", ".")

client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH,
    proxy=(PROXY_SERVER, PROXY_PORT, PROXY_SECRET),
    connection=ConnectionTcpMTProxyRandomizedIntermediate,
    connection_retries=None,
    retry_delay=5,
    auto_reconnect=True,
)


def load_modules():
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    sys.path.insert(0, os.path.dirname(__file__))
    loaded = 0

    for path in sorted(glob.glob(os.path.join(modules_dir, "*.py"))):
        filename = os.path.basename(path)
        if filename.startswith("_"):
            continue

        module_name = f"modules.{filename[:-3]}"
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "register"):
                module.register(client, PREFIX)
            elif hasattr(module, "init"):
                module.init(client)
            log.info("✅ Загружен модуль: %s", filename[:-3])
            loaded += 1
        except Exception:
            log.exception("❌ Ошибка при загрузке %s", filename[:-3])

    log.info("Загружено модулей: %s", loaded)


def print_qr(url: str):
    try:
        import qrcode
    except ImportError:
        log.warning("Пакет qrcode не установлен; используй ссылку ниже")
    else:
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)

    print(f"\n🔗 QR-ссылка: {url}\n")


async def login_via_qr() -> bool:
    log.info("Запускаю QR-вход через MTProxy...")

    try:
        qr_login = await client.qr_login()
        deadline = asyncio.get_running_loop().time() + 60

        while asyncio.get_running_loop().time() < deadline:
            print("\n" + "=" * 50)
            print("  ВХОД ЧЕРЕЗ QR-КОД")
            print("=" * 50)
            print_qr(qr_login.url)
            print(
                "Открой Telegram → Настройки → Устройства → "
                "Подключить устройство"
            )
            print("Отсканируй QR-код. Ожидаю 60 секунд...\n")

            try:
                await asyncio.wait_for(qr_login.wait(), timeout=20)
                log.info("✅ QR-код отсканирован!")
                return True
            except asyncio.TimeoutError:
                if asyncio.get_running_loop().time() < deadline:
                    try:
                        await qr_login.recreate()
                    except Exception:
                        log.exception("Не удалось обновить QR-код")

        log.warning("⏰ Таймаут QR-входа (60 сек).")
        return False
    except SessionPasswordNeededError:
        password = input("Введи пароль двухфакторной аутентификации: ")
        await client.sign_in(password=password)
        return True
    except Exception:
        log.exception("Ошибка QR-входа через MTProxy")
        return False


async def login():
    if await client.is_user_authorized():
        log.info("Найдена сохранённая Telegram-сессия")
        return

    method = os.environ.get("LOGIN_METHOD", "qr").lower()
    if method == "phone":
        log.info("Вход по номеру телефона через MTProxy...")
        await client.start()
        return

    success = await login_via_qr()
    if not success:
        log.info("QR не сработал. Переключаюсь на вход по номеру телефона...")
        await client.start()


async def main():
    log.info("Запускаю юзербота через MTProxy %s:%s", PROXY_SERVER, PROXY_PORT)
    log.info("Сессия: %s", SESSION_NAME)
    log.info("Префикс: %s", PREFIX)

    load_modules()
    await client.connect()
    await login()

    me = await client.get_me()
    log.info("Авторизован как: %s (@%s)", me.first_name, me.username)
    log.info("Юзербот запущен и слушает события.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
