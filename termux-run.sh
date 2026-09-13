#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -f userbot/.env ]]; then
    echo "Нет файла userbot/.env. Сначала запусти ./termux-install.sh" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1091
source userbot/.env
set +a

: "${API_ID:?Заполни API_ID в userbot/.env}"
: "${API_HASH:?Заполни API_HASH в userbot/.env}"
: "${PROXY_SERVER:?Заполни PROXY_SERVER в userbot/.env}"
: "${PROXY_PORT:?Заполни PROXY_PORT в userbot/.env}"
: "${PROXY_SECRET:?Заполни PROXY_SECRET в userbot/.env}"

exec python main.py
