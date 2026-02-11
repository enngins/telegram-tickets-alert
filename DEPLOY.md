# Deploy pe Render.com – pași clari

## Ce ai nevoie înainte

- Cont pe [Render.com](https://dashboard.render.com)
- Repo-ul pe GitHub (deja făcut)
- Fișierul **session.session** în folderul proiectului (l-ai generat când a mers local)

---

## Pasul 1 – Conectează GitHub la Render

1. Mergi la **https://dashboard.render.com**
2. Loghează-te (sau creează cont)
3. Apasă **New +** (sau **Add New**) → **Background Worker**
4. La **Connect a repository**:
   - Dacă nu vezi repo-ul: apasă **Configure account** și dă acces la GitHub (repo-ul **telegram-tickets-alert** sau contul **enngins**)
   - Alege repo-ul **telegram-tickets-alert**
   - Branch: **master** (sau cum l-ai numit tu)
   - Apasă **Connect**

---

## Pasul 2 – Setări de bază ale worker-ului

Completezi câmpurile exact așa:

| Câmp | Valoare |
|------|---------|
| **Name** | `telegram-tickets-alert` (sau orice nume) |
| **Region** | Oregon (sau cel mai apropiat) |
| **Branch** | `master` |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |
| **Plan** | **Starter** (worker-ul nu e gratuit pe Render) |

Nu dai încă **Create**; continuă cu pașii următori.

---

## Pasul 3 – Disc persistent

1. În pagina de creare a worker-ului, caută secțiunea **Disks** (sau **Add Disk**)
2. Apasă **Add Disk**
3. Completezi:
   - **Name:** `state`
   - **Mount Path:** `/data`
   - **Size:** `1` GB
4. Salvezi / lași adăugat

Fără acest disc, `last_id.json` se pierde la fiecare restart.

---

## Pasul 4 – Variabile de mediu (Environment)

1. În aceeași pagină, secțiunea **Environment** sau **Environment Variables**
2. Apasă **Add Environment Variable** și adaugi **câte una** (folosești aceleași valori ca în `.env`):

| Key | Value | Secret? |
|-----|--------|--------|
| `API_ID` | `35603575` (numărul tău) | Da (bifează) |
| `API_HASH` | `35621fa188056ba0e9bc04dba8cd0195` | Da |
| `BOT_TOKEN` | `8506444790:AAE...` (tokenul complet) | Da |
| `CHAT_ID` | `343764189` | Da (opțional) |
| `CHANNEL` | `touristmd` | Nu |

3. Adaugi și aceste două (nu sunt secrete):

| Key | Value |
|-----|--------|
| `STATE_FILE` | `/data/last_id.json` |
| `SESSION_FILE_PATH` | `/etc/secrets/session.session` |

Verifici că nu ai spații în plus la început/sfârșit la Value.

---

## Pasul 5 – Fișierul de sesiune Telegram (Secret File)

Fără acest fișier, worker-ul nu poate citi canalul Telegram.

1. Tot în **Environment**, caută **Secret Files** (sau **Files**, **Mount Secret Files**)
2. Apasă **Add Secret File** (sau **Add File**)
3. Completezi:
   - **Filename (Key):** exact `session.session`
   - **Contents:**  
     - Dacă există buton **Upload**: alegi fișierul **session.session** din `D:\Soft\Python\telegram-tickets-alert\session.session`  
     - Dacă e doar câmp text: deschizi `session.session` în Notepad++ (Encoding: UTF-8 sau binary), copiezi tot și lipești (uneori Render acceptă doar text; dacă dă eroare, folosești Upload dacă apare)

Pe Render fișierul va fi montat la `/etc/secrets/session.session`; de aceea ai setat `SESSION_FILE_PATH=/etc/secrets/session.session`.

---

## Pasul 6 – Creare worker și primul deploy

1. Apasă **Create Background Worker** (sau **Deploy**)
2. Render va:
   - clona repo-ul
   - rula `pip install -r requirements.txt`
   - rula `python main.py`
3. Mergi la **Logs** (tab-ul **Logs** al worker-ului)
4. Ar trebui să vezi ceva de genul:
   - `Sesiune copiată din /etc/secrets/session.session`
   - `Pornit poll la fiecare 300 secunde`
   - (la fiecare ~5 min) mesaje de tip „Alert trimis…” dacă găsește oferte

Dacă în Logs apare eroare (ex. „Lipsește API_ID”, „Session invalid”), revino la **Environment** și la **Secret File** și verifici valorile și fișierul.

---

## După deploy

- **Auto-deploy:** la fiecare push pe branch-ul conectat (ex. `master`), Render poate face deploy automat (opțiune în Settings).
- **Logs:** mereu din tab-ul **Logs** vezi ce face aplicația.
- **Oprire:** din Dashboard poți opri worker-ul (nu mai consumă credite), sau îl lași pornit ca să primești alerte continuu.

---

## Rezumat rapid

1. New → Background Worker → conectezi repo-ul.
2. Build: `pip install -r requirements.txt`, Start: `python main.py`, Plan: Starter.
3. Add Disk: mount path `/data`, 1 GB.
4. Environment: `API_ID`, `API_HASH`, `BOT_TOKEN`, `CHAT_ID`, `CHANNEL`, plus `STATE_FILE` și `SESSION_FILE_PATH`.
5. Secret File: `session.session` = fișierul tău local (upload sau paste).
6. Create Worker → verifici Logs.

Gata.
