import os
import sys
import json
import time
import logging
import shutil
import requests
import unicodedata
from telethon.sync import TelegramClient
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# -----------------------
# Load ENV (DOTENV_PATH din run.bat, altfel lângă script, apoi .env în cwd)
# -----------------------
_env_path = os.environ.get("DOTENV_PATH")
if not _env_path:
    _base = os.path.dirname(os.path.abspath(__file__))
    _env_path = os.path.join(_base, ".env")
load_dotenv(_env_path, encoding="utf-8-sig")
if not os.environ.get("API_ID"):
    load_dotenv(".env", encoding="utf-8-sig")

def _getenv(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"Lipsește {name}. Setează în .env sau variabilă de mediu.")
    return v

API_ID = int(_getenv("API_ID"))
API_HASH = _getenv("API_HASH")
BOT_TOKEN = _getenv("BOT_TOKEN")
CHAT_ID = _getenv("CHAT_ID")
CHANNEL = _getenv("CHANNEL")

# Pe Render: setează STATE_FILE=/data/last_id.json și montează disk la /data
STATE_FILE = os.environ.get("STATE_FILE", "last_id.json")
# Pe Render: Secret File "session.session" e montat la /etc/secrets/session.session
SESSION_FILE_PATH = os.environ.get("SESSION_FILE_PATH")

# -----------------------
# Keywords (RO + RU + EN)
# -----------------------
KEYWORDS = [
    "paris",
    "париж",
    "cdg",
    "ory",
    "charles de gaulle",
    "orly"
]


# -----------------------
# Helpers
# -----------------------
def normalize_text(text: str) -> str:
    """
    Lowercase + remove diacritics for safer matching
    """
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text


REDIS_KEY = "telegram_tickets:last_id"
_redis = None

def _get_redis():
    global _redis
    if _redis is not None:
        return _redis
    url = os.environ.get("UPSTASH_REDIS_REST_URL")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
    if url and token:
        try:
            from upstash_redis import Redis
            _redis = Redis(url=url, token=token)
            return _redis
        except Exception as e:
            log.warning("Redis indisponibil, folosesc fișier: %s", e)
    return None

def load_last_id():
    r = _get_redis()
    if r:
        try:
            v = r.get(REDIS_KEY)
            return int(v) if v else 0
        except Exception as e:
            log.warning("Redis get eșuat: %s", e)
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("last_id", 0)
    return 0

def save_last_id(last_id):
    r = _get_redis()
    if r:
        try:
            r.set(REDIS_KEY, str(last_id))
            return
        except Exception as e:
            log.warning("Redis set eșuat: %s", e)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_id": last_id}, f)


def send_telegram_message(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        log.exception("Trimitere Telegram eșuată: %s", e)
        return False


def contains_keyword(text: str) -> bool:
    normalized = normalize_text(text)
    return any(keyword in normalized for keyword in KEYWORDS)


# -----------------------
# Main Logic
# -----------------------
def run_once():
    last_processed_id = load_last_id()
    new_last_id = last_processed_id

    try:
        with TelegramClient("session", API_ID, API_HASH) as client:
            # min_id ca să nu pierzi mesaje dacă sunt multe
            messages = client.get_messages(
                CHANNEL, limit=100, min_id=last_processed_id
            )

            for msg in reversed(messages):
                if msg.id <= last_processed_id:
                    continue
                new_last_id = max(new_last_id, msg.id)

                if msg.text and contains_keyword(msg.text):
                    alert_text = (
                        "🔥 Ofertă Paris găsită!\n\n"
                        f"{msg.text}\n\n"
                        f"Link: https://t.me/{CHANNEL.replace('@', '')}/{msg.id}"
                    )
                    if send_telegram_message(alert_text):
                        log.info("Alert trimis pentru msg id=%s", msg.id)

        save_last_id(new_last_id)
    except Exception as e:
        log.exception("Eroare run: %s", e)
        sys.exit(1)


def _ensure_session():
    """Sesiune: din SESSION_B64 (base64, GitHub Actions), din SESSION_FILE_PATH (Render), sau fișier local."""
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.session")
    b64 = os.environ.get("SESSION_B64")
    if b64:
        import base64
        try:
            data = base64.b64decode(b64)
            with open(dest, "wb") as f:
                f.write(data)
            log.info("Sesiune scrisă din SESSION_B64")
            return
        except Exception as e:
            log.warning("SESSION_B64 invalid: %s", e)
    if SESSION_FILE_PATH and os.path.isfile(SESSION_FILE_PATH):
        if os.path.abspath(SESSION_FILE_PATH) != os.path.abspath(dest):
            shutil.copy(SESSION_FILE_PATH, dest)
            log.info("Sesiune copiată din %s", SESSION_FILE_PATH)


def main():
    _ensure_session()

    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true", help="Rulează o singură dată și iese")
    p.add_argument(
        "--interval",
        type=int,
        default=int(os.environ.get("INTERVAL_SEC", "300")),
        help="Secunde între rulări",
    )
    args = p.parse_args()

    if args.once:
        run_once()
        return

    log.info("Pornit poll la fiecare %s secunde (Ctrl+C oprește)", args.interval)
    while True:
        run_once()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
