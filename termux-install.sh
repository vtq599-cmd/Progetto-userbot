#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

pkg update -y
pkg install -y python git ffmpeg
python -m pip install --upgrade pip
python -m pip install -r requirements-termux.txt

if [[ ! -f userbot/.env ]]; then
    cp termux.env.example userbot/.env
    chmod 600 userbot/.env
    echo "Создан userbot/.env — заполни API_ID, API_HASH и данные MTProxy."
fi

echo "Установка завершена. Запусти: ./termux-run.sh"
