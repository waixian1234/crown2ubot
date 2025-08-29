# Crown2u Telegram Bot (Webhook, Render-ready)

Webhook-based Telegram bot that mirrors your **Nanas44** feature set:

- ✅ `/start` welcome with buttons (channel + group) and optional banner image
- ✅ Store subscribers in `subscribers.txt`
- ✅ Admin commands: `/subcount`, `/export_subscribers`, `/broadcast`
- ✅ Forward channel posts to the bot → auto fanout to all subscribers
  - Uses **copy_message from the original channel** so subscribers see "Forwarded from <Channel>" (no double forward)
- ✅ Daily 00:00 (Asia/Kuala_Lumpur) auto-backup of `subscribers.txt` to all Admin IDs
- ✅ Rate limiting between sends via `DELAY` (default 0.5s)

---

## Environment variables

| Name              | Required | Example / Notes |
|-------------------|----------|-----------------|
| `BOT_TOKEN`       | ✅ | Your Telegram bot token |
| `WEBHOOK_URL`     | ✅ | Public HTTPS URL, e.g. `https://YOUR-RENDER-SERVICE.onrender.com/webhook` |
| `PORT`            | auto     | Render sets this automatically |
| `ADMIN_IDS`       | optional | Comma-separated extra admin IDs. Defaults already include `1840751528,1280460690` |
| `CHANNEL_BUTTON_TEXT` | optional | Text for channel button |
| `CHANNEL_URL`     | optional | `https://t.me/nanas44` |
| `GROUP_BUTTON_TEXT` | optional | Text for group button |
| `GROUP_URL`       | optional | `https://t.me/addlist/OyQ3Pns_j3w5Y2M1` |
| `WELCOME_IMAGE`   | optional | `banner-01.png` in project root |
| `SUBSCRIBER_FILE` | optional | Defaults to `subscribers.txt` |
| `LOG_DIR`         | optional | Defaults to `logs` |
| `DELAY`           | optional | Seconds between fanout messages, default `0.5` |
| `TZ`              | optional | Defaults `Asia/Kuala_Lumpur` |

---

## Deploy to Render

1. Push this repo to GitHub.
2. Create a **Web Service** in Render: *New → Web Service → Connect repo*.
3. **Environment**: Python 3.11+.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `python main.py`
6. Add **Environment Variables**:
   - `BOT_TOKEN` = your bot token
   - `WEBHOOK_URL` = your Render service URL + `/webhook`
   - `ADMIN_IDS` = 1840751528,1280460690,1873662628
7. Check Render Logs: should show `Bot webhook running on port ...`.

---

## Usage

- `/start` → stores subscriber + sends welcome banner/buttons.
- `/subcount` → number of subscribers.
- `/export_subscribers` → sends `subscribers.txt`.
- `/broadcast <text>` or reply with `/broadcast` → send to all.
- Forward channel posts → auto fanout to all subscribers (keeps "Forwarded from Channel").
- Daily 00:00 MYT → auto backup `subscribers.txt` to admins.

---

## File tree
