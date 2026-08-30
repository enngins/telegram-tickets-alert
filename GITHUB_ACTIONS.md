# GitHub Actions + Upstash Redis

This deployment method allows the ticket alert to run automatically using **GitHub Actions** and **Upstash Redis**.

The workflow runs approximately every **5 minutes**, while Upstash Redis is used to persist the `last_id` state between workflow runs.

This approach is suitable if you want a simple, low-cost deployment without maintaining a permanent server.

---

## 1. Create an Upstash Redis Database

1. Go to [Upstash](https://upstash.com) and sign up or log in.
2. Create a new database.
3. Select the **Free** plan.
4. Choose a region close to your users or your deployment.
5. Open the database dashboard and go to **REST API**.
6. Copy the following values:

```text
UPSTASH_REDIS_REST_URL
UPSTASH_REDIS_REST_TOKEN
```

You will add both values as GitHub repository secrets later.

---

## 2. Convert the Telegram Session to Base64

The application requires the Telegram session file:

```text
session.session
```

If you have already authenticated successfully when running the project locally, this file should already exist.

GitHub Actions cannot use the local file directly, so we convert it to Base64 and store it securely as a GitHub Secret.

### Windows PowerShell

Run this command from the project directory:

```powershell
[Convert]::ToBase64String(
    [IO.File]::ReadAllBytes("$PWD\session.session")
)
```

Copy the entire output.

It should be a single long line.

You will use this value as:

```text
SESSION_B64
```

> Treat the Base64 session value as a credential. Do not publish it or commit it to Git.

---

## 3. Configure GitHub Secrets

Open your repository:

**Settings → Secrets and variables → Actions**

Click:

**New repository secret**

Add the following secrets:

| Secret                     | Description                        |
| -------------------------- | ---------------------------------- |
| `API_ID`                   | Telegram API ID                    |
| `API_HASH`                 | Telegram API hash                  |
| `BOT_TOKEN`                | Telegram bot token                 |
| `CHAT_ID`                  | Destination chat ID                |
| `CHANNEL`                  | Telegram channel/source to monitor |
| `UPSTASH_REDIS_REST_URL`   | Upstash REST API URL               |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash REST API token             |
| `SESSION_B64`              | Base64-encoded `session.session`   |

Do not put actual credentials directly into the workflow file.

---

## 4. Push and Verify

Make sure the GitHub Actions workflow exists in:

```text
.github/workflows/run-alert.yml
```

Push it to your repository.

Then:

1. Open the repository's **Actions** tab.
2. Select **Telegram tickets alert**.
3. The workflow should run automatically according to its schedule.
4. You can also use **Run workflow** to trigger it manually.
5. Open the workflow run to inspect the logs.

The logs can be used to verify:

* Telegram session initialization
* Redis connectivity
* Polling
* Ticket detection
* Telegram alerts

---

## How It Works

```text
GitHub Actions
      │
      │ every ~5 minutes
      ▼
Telegram Tickets Alert
      │
      ├── Read Telegram session
      ├── Check for new tickets
      ├── Read previous state
      └── Send alert if needed
               │
               ▼
           Telegram

          ▲
          │
          │ persistent state
          │
     Upstash Redis
```

---

## Session Renewal

If your Telegram session becomes invalid, or you intentionally delete/reset the session:

1. Authenticate locally again.
2. Generate a new `session.session`.
3. Convert it to Base64.
4. Replace the `SESSION_B64` GitHub Secret.

After updating the secret, run the workflow manually to verify that the new session works.

---

## Quick Checklist

* [ ] Upstash account created
* [ ] Redis database created
* [ ] `UPSTASH_REDIS_REST_URL` copied
* [ ] `UPSTASH_REDIS_REST_TOKEN` copied
* [ ] `session.session` generated locally
* [ ] Session converted to Base64
* [ ] All 8 GitHub Secrets configured
* [ ] `.github/workflows/run-alert.yml` pushed
* [ ] GitHub Actions workflow tested successfully
