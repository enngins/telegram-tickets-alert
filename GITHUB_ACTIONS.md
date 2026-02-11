# Rulare gratuită cu GitHub Actions + Upstash Redis

Alert-ul rulează la fiecare **5 minute** pe GitHub Actions (gratuit). State-ul `last_id` se păstrează în **Upstash Redis** (plan gratuit).

---

## 1. Cont Upstash Redis (gratuit)

1. Mergi la **[upstash.com](https://upstash.com)** → Sign up / Log in.
2. **Create Database** → alege regiunea (ex. eu-central-1), **Free** plan → Create.
3. În dashboard-ul bazei: tab **REST API** (sau **.env**).
4. Copiază:
   - **UPSTASH_REDIS_REST_URL** (URL-ul HTTPS)
   - **UPSTASH_REDIS_REST_TOKEN** (token-ul)

Le vei pune în Secrets pe GitHub la pasul 3.

---

## 2. Obține SESSION_B64 (sesiunea Telegram în base64)

Ai deja fișierul **session.session** în proiect (după ce a mers local). Îl transformi în base64 ca să îl pui într-un secret.

**În PowerShell** (din folderul proiectului):

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$PWD\session.session")) | Set-Clipboard
```

Conținutul base64 e acum în clipboard. Sau fără clipboard, doar afișat:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$PWD\session.session"))
```

Copiază **tot** output-ul (o singură linie lungă) – va deveni valoarea secretului **SESSION_B64**.

---

## 3. Secrets în GitHub

1. Repo-ul tău → **Settings** → **Secrets and variables** → **Actions**.
2. **New repository secret** și adaugi fiecare:

| Nume secret | Valoare |
|--------------|---------|
| `API_ID` | din .env (ex. 35603575) |
| `API_HASH` | din .env |
| `BOT_TOKEN` | din .env |
| `CHAT_ID` | din .env |
| `CHANNEL` | din .env (ex. touristmd) |
| `UPSTASH_REDIS_REST_URL` | URL din Upstash (pasul 1) |
| `UPSTASH_REDIS_REST_TOKEN` | Token din Upstash |
| `SESSION_B64` | linia lungă base64 de la pasul 2 |

---

## 4. Push și verificare

1. Fă push la branch-ul tău (inclusiv fișierul `.github/workflows/run-alert.yml`).
2. În repo: tab **Actions** → workflow **Telegram tickets alert**.
3. Rulează automat la fiecare 5 min sau apasă **Run workflow** pentru o rulare imediată.
4. Deschizi o rulare → **run** → **Run alert once**: acolo vezi log-urile (sesiune, Redis, alerte trimise).

---

## Rezumat

- **Upstash**: cont gratuit → 1 DB → copiezi URL + token.
- **SESSION_B64**: base64 din `session.session` (PowerShell mai sus).
- **GitHub Secrets**: cele 8 chei de mai sus.
- **Push** → Actions rulează la fiecare 5 min.

Dacă schimbi parola Telegram sau ștergi sesiunea, trebuie regenerat **session.session** local și din nou **SESSION_B64** + actualizat secretul.
