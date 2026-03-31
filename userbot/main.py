import os
import sys
import glob                                                           import importlib
import asyncio
import logging                                                        
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.network.connection import ConnectionTcpMTProxyRandomizedIntermediate
from config import API_ID, API_HASH, SESSION_NAME, PROXY_SERVER, PROXY_PORT, PROXY_SECRET

logging.basicConfig(                                                      level=logging.INFO,
    format="[%(asctime)s] %(levelname)s — %(message)s",                   datefmt="%H:%M:%S"
)
log = logging.getLogger("userbot")

PREFIX = os.environ.get("BOT_PREFIX", ".")

proxy = (PROXY_SERVER, PROXY_PORT, PROXY_SECRET)

client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH,
    proxy=proxy,
    connection=ConnectionTcpMTProxyRandomizedIntermediate
)

                                                                      def load_modules():                                                       modules_dir = os.path.join(os.path.dirname(__file__), "modules")      sys.path.insert(0, os.path.dirname(__file__))                                                                                               module_files = glob.glob(os.path.join(modules_dir, "*.py"))           loaded = 0                                                                                                                                  for path in sorted(module_files):                                         filename = os.path.basename(path)                                     if filename.startswith("_"):
            continue

        module_name = f"modules.{filename[:-3]}"                              try:
            mod = importlib.import_module(module_name)                            if hasattr(mod, "register"):
                mod.register(client, PREFIX)
            elif hasattr(mod, "init"):                                                mod.init(client)
            log.info(f"✅ Загружен модуль: {filename[:-3]}")                      loaded += 1
        except Exception as e:
            log.error(f"❌ Ошибка при загрузке {filename[:-3]}: {e}")

    log.info(f"Загружено модулей: {loaded}")


def print_qr(url: str):
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)                                       except ImportError:
        log.warning("Установи qrcode: pip install qrcode")            
    print(f"\n🔗 QR-ссылка: {url}\n")
                                                                      
async def login_via_qr() -> bool:                                         log.info("Запускаю QR-вход...")

    try:
        qr_login = await client.qr_login()
                                                                              print("\n" + "=" * 50)                                                print("  ВХОД ЧЕРЕЗ QR-КОД")                                          print("=" * 50)                                                       print_qr(qr_login.url)                                                print("Открой Telegram → Настройки → Устройства → Подключить устройство")                                                                   print("Отсканируй QR-код. Ожидаю 60 секунд...\n")                                                                                           deadline = asyncio.get_event_loop().time() + 60                       while asyncio.get_event_loop().time() < deadline:                         try:                                                                      await asyncio.wait_for(qr_login.wait(), timeout=20)                   log.info("✅ QR-код отсканирован!")                                   return True                                                       except asyncio.TimeoutError:                                              if asyncio.get_event_loop().time() < deadline:                            try:                                                                      await qr_login.recreate()                                             print("\nQR-код обновлён:")                                           print_qr(qr_login.url)                                            except Exception:                                                         pass
            except SessionPasswordNeededError:                                        password = input("Введи пароль двухфакторной аутентификации: ")                                                                             await client.sign_in(password=password)
                return True
                                                                              log.warning("⏰ Таймаут QR-входа (60 сек).")
        return False                                                  
    except Exception as e:                                                    log.error(f"Ошибка QR-входа: {e}")
        return False                                                  

async def login():                                                        if await client.is_user_authorized():
        return                                                                                                                                  method = os.environ.get("LOGIN_METHOD", "qr").lower()
                                                                          if method == "phone":
        log.info("Вход по номеру телефона...")
        await client.start()
        return

    success = await login_via_qr()                                        if not success:
        log.info("QR не сработал. Переключаюсь на вход по номеру телефона...")
        await client.start()
                                                                      
async def main():                                                         log.info("Запускаю юзербота...")
    log.info(f"MTProxy: {PROXY_SERVER}:{PROXY_PORT}")
    load_modules()

    await client.connect()                                                await login()                                                                                                                               me = await client.get_me()                                            log.info(f"Авторизован как: {me.first_name} (@{me.username})")        log.info(f"Префикс: {PREFIX}")                                        log.info("Юзербот запущен и слушает события.")                                                                                              await client.run_until_disconnected()                                                                                                                                                                         if __name__ == "__main__":                                                asyncio.run(main())