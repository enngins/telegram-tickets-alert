# Deploy to Render

This guide explains how to deploy **Telegram Tickets Alert** as a Render Background Worker.

Unlike the GitHub Actions deployment, a Render worker can run continuously and does not depend on a scheduled workflow.

---

## Before You Start

You will need:

* A [Render](https://render.com) account
* The GitHub repository
* A working `session.session` file generated locally
* Your Telegram API credentials
* Your Telegram bot token

> Keep your Telegram credentials and session file private. Do not commit them to Git.

---

## 1. Connect GitHub to Render

1. Open the Render dashboard.
2. Log in or create an account.
3. Select **New → Background Worker**.
4. Under **Connect a repository**, connect your GitHub account if necessary.
5. Select the `telegram-tickets-alert` repository.
6. Select the branch you want to deploy, for example:

```text
master
```

7. Click **Connect**.

---

## 2. Configure the Background Worker

Use the following configuration:

| Setting           | Value                                        |
| ----------------- | -------------------------------------------- |
| **Name**          | `telegram-tickets-alert`                     |
| **Region**        | Choose a region close to your users          |
| **Branch**        | `master`                                     |
| **Runtime**       | Python 3                                     |
| **Build Command** | `pip install -r requirements.txt`            |
| **Start Command** | `python main.py`                             |
| **Plan**          | Starter or another suitable paid worker plan |

> Render Background Workers are not available as a permanently free service, so choose the plan appropriate for your usage.

Do not deploy yet. Configure the persistent disk and environment variables first.

---

## 3. Add a Persistent Disk

The application uses `last_id.json` to remember its previous state.

Without persistent storage, this file may be lost when the worker restarts.

In the worker configuration:

1. Find **Disks** or **Add Disk**.
2. Add a new disk.
3. Configure it as follows:

| Setting        | Value   |
| -------------- | ------- |
| **Name**       | `state` |
| **Mount Path** | `/data` |
| **Size**       | `1 GB`  |

The application will then use:

```text
/data/last_id.json
```

for persistent state.

---

## 4. Configure Environment Variables

Open **Environment** / **Environment Variables** and add the following values.

| Variable            | Description                    | Secret   |
| ------------------- | ------------------------------ | -------- |
| `API_ID`            | Telegram API ID                | Yes      |
| `API_HASH`          | Telegram API hash              | Yes      |
| `BOT_TOKEN`         | Telegram bot token             | Yes      |
| `CHAT_ID`           | Destination chat ID            | Optional |
| `CHANNEL`           | Telegram channel/source        | No       |
| `STATE_FILE`        | `/data/last_id.json`           | No       |
| `SESSION_FILE_PATH` | `/etc/secrets/session.session` | No       |

For example:

```env
STATE_FILE=/data/last_id.json
SESSION_FILE_PATH=/etc/secrets/session.session
```

Make sure there are no accidental spaces before or after the values.

---

## 5. Add the Telegram Session as a Secret File

The Telegram session is required for the application to access the configured Telegram source.

In Render:

1. Open **Environment**.
2. Find **Secret Files** / **Files**.
3. Select **Add Secret File**.
4. Set the filename to exactly:

```text
session.session
```

5. Upload your local `session.session` file.

Render will make the file available at:

```text
/etc/secrets/session.session
```

which matches:

```env
SESSION_FILE_PATH=/etc/secrets/session.session
```

> Do not commit `session.session` to GitHub.

---

## 6. Deploy the Worker

Once the configuration is complete:

1. Click **Create Background Worker** / **Deploy**.
2. Render will clone the repository.
3. It will install the dependencies:

```bash
pip install -r requirements.txt
```

4. It will start the application:

```bash
python main.py
```

5. Open the worker's **Logs** tab.

You should see messages indicating that the application has initialized successfully and started polling.

Depending on the current logging configuration, you may see messages related to:

* Telegram session initialization
* Polling interval
* Redis/state initialization
* Ticket detection
* Alerts being sent

---

## After Deployment

### Automatic deployments

Render can automatically deploy new commits whenever you push to the connected branch.

This can be enabled in the worker's settings.

### Logs

Use the **Logs** tab to monitor the application and diagnose errors.

### Stopping the worker

You can stop the worker from the Render dashboard when you do not need monitoring.

Start it again when you want to resume continuous monitoring.

---

## Troubleshooting

### Missing environment variables

If the logs indicate that `API_ID`, `API_HASH`, `BOT_TOKEN`, or another variable is missing:

1. Open **Environment**.
2. Check the variable name.
3. Check its value.
4. Make sure there are no leading or trailing spaces.

### Invalid Telegram session

If you see an authentication/session error:

1. Run the application locally.
2. Authenticate with Telegram again.
3. Generate a new `session.session`.
4. Replace the Secret File in Render.
5. Restart/redeploy the worker.

### State resets after restart

Make sure the persistent disk exists and is mounted at:

```text
/data
```

and that:

```env
STATE_FILE=/data/last_id.json
```

is configured correctly.

---

## Quick Checklist

* [ ] GitHub repository connected
* [ ] Background Worker created
* [ ] Python runtime configured
* [ ] Build command configured
* [ ] Start command configured
* [ ] Persistent disk mounted at `/data`
* [ ] Telegram environment variables configured
* [ ] `STATE_FILE` configured
* [ ] `SESSION_FILE_PATH` configured
* [ ] `session.session` uploaded as a Secret File
* [ ] Worker deployed
* [ ] Logs checked

Once these steps are complete, the worker should continue monitoring the configured source and send Telegram notifications when matching tickets become available.
