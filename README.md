# 🎫 Telegram Tickets Alert

**Telegram Tickets Alert** is a lightweight Python service that monitors ticket availability and sends an instant Telegram notification when tickets become available.

It is designed for situations where tickets sell out quickly and manually refreshing a website is simply not practical.

> **No more refreshing. Get notified when something becomes available.**

---

## ✨ Features

* ⚡ **Instant Telegram notifications** when tickets become available
* 🔄 **Configurable polling interval**
* 🛡️ **Retries and rate limiting** for more reliable monitoring
* 🔐 **Environment-based configuration** — keep credentials outside your source code
* 📊 **Structured logging** for monitoring and troubleshooting
* 💾 **Persistent state** to avoid processing the same ticket/message repeatedly
* ☁️ **Multiple deployment options**

  * GitHub Actions + Upstash Redis
  * Render Background Worker

---

## 🧠 How It Works

At a high level, the application works like this:

```text
Target source
     │
     ▼
Telegram Tickets Alert
     │
     ├── Check for new/available tickets
     │
     ├── Compare with previously processed state
     │
     └── Send notification
              │
              ▼
          Telegram
```

The application periodically checks the configured source, detects relevant changes, and sends an alert through Telegram when something new is found.

A small amount of persistent state is stored so that the same alert is not repeatedly sent after every restart.

---

## 🛠️ Tech Stack

* **Python 3.10+**
* **Telegram Bot API**
* **Telegram client/session**
* `httpx`
* `requests`
* `BeautifulSoup4`
* `Playwright`
* `asyncio` / `APScheduler`
* **Upstash Redis** for state persistence in the GitHub Actions deployment

---

# 🚀 Getting Started

## Requirements

Before running the project, make sure you have:

* Python 3.10 or newer
* A Telegram account
* A Telegram bot
* Telegram API credentials
* Access to the Telegram channel/source you want to monitor
* Git

---

## 1. Clone the repository

```bash
git clone https://github.com/enngins/telegram-tickets-alert.git
cd telegram-tickets-alert
```

---

## 2. Install dependencies

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

If the project uses Playwright, install its browser dependencies as required by your environment.

---

# ⚙️ Configuration

The application is configured through environment variables.

Create a `.env` file locally and provide the required values:

```env
API_ID=YOUR_API_ID
API_HASH=YOUR_API_HASH
BOT_TOKEN=YOUR_BOT_TOKEN
CHAT_ID=YOUR_CHAT_ID
CHANNEL=YOUR_CHANNEL

STATE_FILE=last_id.json
SESSION_FILE_PATH=session.session
```

### Configuration reference

| Variable            | Description                           |
| ------------------- | ------------------------------------- |
| `API_ID`            | Telegram API ID                       |
| `API_HASH`          | Telegram API hash                     |
| `BOT_TOKEN`         | Telegram bot token                    |
| `CHAT_ID`           | Destination chat ID for alerts        |
| `CHANNEL`           | Telegram channel/source to monitor    |
| `STATE_FILE`        | Location of the persistent state file |
| `SESSION_FILE_PATH` | Path to the Telegram session file     |

> **Never commit `.env`, `session.session`, or other credentials to Git.**

---

# 🔑 Telegram Session

The application uses a Telegram session file to authenticate the Telegram client.

After successfully authenticating locally, you should have:

```text
session.session
```

Keep this file private.

It should **not** be committed to the repository or shared publicly.

For deployment, the session is provided securely through the deployment platform rather than stored in Git.

---

# 💻 Running Locally

Once your environment is configured:

```bash
python main.py
```

The application will start monitoring according to the configured polling interval.

Check the console output for connection status, polling activity, errors, and alerts.

---

# ☁️ Deployment

There are two supported deployment approaches.

## Option 1 — GitHub Actions + Upstash Redis

This is the **free / low-cost deployment option**.

The GitHub Actions workflow runs the alert approximately every **5 minutes**. Upstash Redis is used to persist the `last_id` state between workflow runs.

### What you need

1. A free Upstash Redis database
2. Your Telegram credentials
3. A base64-encoded `session.session`
4. GitHub repository secrets
5. The workflow:

```text
.github/workflows/run-alert.yml
```

### GitHub Secrets

Configure these repository secrets:

| Secret                     | Description                     |
| -------------------------- | ------------------------------- |
| `API_ID`                   | Telegram API ID                 |
| `API_HASH`                 | Telegram API hash               |
| `BOT_TOKEN`                | Telegram bot token              |
| `CHAT_ID`                  | Destination chat ID             |
| `CHANNEL`                  | Telegram channel/source         |
| `UPSTASH_REDIS_REST_URL`   | Upstash REST API URL            |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash REST API token          |
| `SESSION_B64`              | Base64-encoded Telegram session |

To convert the local session file to Base64 on Windows PowerShell:

```powershell
[Convert]::ToBase64String(
    [IO.File]::ReadAllBytes("$PWD\session.session")
)
```

Copy the complete output and use it as the value of `SESSION_B64`.

After pushing the workflow to GitHub:

1. Open **Actions**
2. Select **Telegram tickets alert**
3. Run it manually with **Run workflow**, or wait for the scheduled run
4. Open the workflow run and inspect **Run alert once** logs

The workflow is configured to run approximately every five minutes.

For the complete GitHub Actions setup, see:

**[GITHUB_ACTIONS.md](./GITHUB_ACTIONS.md)**

---

## Option 2 — Render Background Worker

For continuous monitoring, the project can also run as a **Render Background Worker**.

The worker runs:

```bash
pip install -r requirements.txt
```

and starts the application with:

```bash
python main.py
```

The Render deployment requires a persistent disk because the application stores state in `last_id.json`.

### Recommended configuration

| Setting             | Value                             |
| ------------------- | --------------------------------- |
| Runtime             | Python 3                          |
| Build Command       | `pip install -r requirements.txt` |
| Start Command       | `python main.py`                  |
| Disk Mount Path     | `/data`                           |
| Disk Size           | 1 GB                              |
| `STATE_FILE`        | `/data/last_id.json`              |
| `SESSION_FILE_PATH` | `/etc/secrets/session.session`    |

The Telegram session should be uploaded as a **Render Secret File** named:

```text
session.session
```

Render then mounts it at:

```text
/etc/secrets/session.session
```

The corresponding environment variable should therefore be:

```env
SESSION_FILE_PATH=/etc/secrets/session.session
```

For the complete Render deployment walkthrough, see:

**[DEPLOY.md](./DEPLOY.md)**

---

# 📊 Monitoring

The application logs important runtime information, including:

* Telegram session status
* Redis/state status
* Polling activity
* Errors and connection problems
* Alerts that have been sent

When deployed to Render, these logs are available from the worker's **Logs** tab.

When using GitHub Actions, logs are available directly inside the workflow run.

---

# 🔧 Troubleshooting

### `API_ID` or other environment variable is missing

Check that all required environment variables/secrets are configured correctly.

### `Session invalid`

Your Telegram session may have expired or been invalidated.

Generate a new `session.session` locally and update the deployment secret.

For GitHub Actions, regenerate the Base64 value and replace:

```text
SESSION_B64
```

For Render, replace the deployed Secret File.

### Alerts are duplicated

Make sure the state storage is configured correctly.

For Render, verify that:

```text
STATE_FILE=/data/last_id.json
```

and that the `/data` persistent disk is attached.

For GitHub Actions, verify that the Upstash Redis credentials are correct.

### GitHub Actions is not running

Check:

* `.github/workflows/run-alert.yml` exists
* The workflow is pushed to GitHub
* The repository's **Actions** tab is enabled
* Repository secrets are configured
* The workflow schedule is active

---

# 🔐 Security

This project interacts with Telegram credentials and authentication data.

**Do not commit or publish:**

```text
.env
session.session
BOT_TOKEN
API_HASH
SESSION_B64
UPSTASH_REDIS_REST_TOKEN
```

If a credential is accidentally exposed, revoke or regenerate it immediately.

For GitHub Actions, use **Repository Secrets**.

For Render, use **Environment Variables** and **Secret Files**.

---

# 📁 Project Structure

```text
telegram-tickets-alert/
│
├── .github/
│   └── workflows/
│       └── run-alert.yml
│
├── main.py
├── requirements.txt
├── render.yaml
├── run.bat
│
├── GITHUB_ACTIONS.md
├── DEPLOY.md
└── README.md
```

---

# 🤝 Contributing

Contributions, improvements, bug reports, and ideas are welcome.

If you find a problem or have an idea for improving the project, feel free to open an issue or submit a pull request.

---


## ⭐ If this project is useful to you

If Telegram Tickets Alert saves you from repeatedly refreshing ticket pages, consider giving the repository a ⭐.

It helps the project get discovered by other people who may find it useful.
