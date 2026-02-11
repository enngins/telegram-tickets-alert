# Deploy pe Render.com

## 1. Sesiune Telethon (o singură dată, local)

Rulezi local o dată ca să se creeze `session.session` (login Telegram):

```bash
python main.py --once
```

Introduci număr, cod etc. După succes, în proiect apare `session.session`. **Nu pui acest fișier în Git.**

## 2. Repo pe GitHub

- Fă push la un repo (GitHub/GitLab).
- Asigură-te că în `.gitignore` ai: `.env`, `session.session`, `last_id.json`, `__pycache__/`.

## 3. Render – serviciu nou

1. [dashboard.render.com](https://dashboard.render.com) → **New** → **Background Worker**.
2. Conectezi repo-ul și branch-ul.
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `python main.py`
5. **Plan:** Starter (worker-ii nu au free tier).

## 4. Disc persistent

În worker: **Disks** → **Add Disk**:

- **Mount Path:** `/data`
- **Size:** 1 GB

(Alternativ, dacă folosești Blueprint din `render.yaml`, discul e deja definit acolo.)

## 5. Variabile de mediu

În **Environment** adaugi (ca **Secret** unde e sensibile):

- `API_ID` – număr (ex: 12345678)
- `API_HASH` – string
- `BOT_TOKEN` – tokenul botului Telegram
- `CHAT_ID` – id-ul chat-ului unde trimite alertă
- `CHANNEL` – username-ul canalului (ex: `touristmd` sau `@touristmd`)

Nu trebuie să pui `STATE_FILE` și `SESSION_FILE_PATH` dacă folosești Blueprint; sunt setate în `render.yaml`.

## 6. Secret File pentru sesiune

Fără asta, pe Render nu poți face login interactiv, deci folosești sesiunea generată local:

1. În worker: **Environment** → **Secret Files** (sau **Files**).
2. **Add Secret File**:
   - **Filename:** `session.session`
   - **Contents:** conținutul fișierului `session.session` de pe mașina ta (îl deschizi cu un editor binar/text și copiezi tot).

Pe Render fișierul va fi montat la `/etc/secrets/session.session`. Aplicația citește `SESSION_FILE_PATH` (setat în Blueprint la `/etc/secrets/session.session`) și copiază sesiunea în directorul de lucru înainte de a folosi Telethon.

## 7. Deploy

Dai **Deploy** (sau la push se face auto-deploy dacă e activat). În **Logs** ar trebui să vezi „Sesiune copiată…” și apoi ciclul de polling.

## Rezumat

- **Worker** = proces care rulează continuu și execută `python main.py` (loop cu `time.sleep(INTERVAL_SEC)`).
- **Disc** la `/data` = acolo se salvează `last_id.json` (via `STATE_FILE=/data/last_id.json`).
- **Secret File** `session.session` = sesiunea Telethon făcută local, montată pe Render la `/etc/secrets/session.session`.

Dacă nu folosești Blueprint și creezi worker-ul manual, în **Environment** adaugi și:

- `STATE_FILE` = `/data/last_id.json`
- `SESSION_FILE_PATH` = `/etc/secrets/session.session`

(și montezi discul la `/data` și Secret File ca mai sus).
