import os
import logging
import asyncio
from datetime import time as dtime
from zoneinfo import ZoneInfo

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ---------------------- Configuration ----------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "")  # REQUIRED
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # REQUIRED: e.g. https://your-domain.onrender.com/webhook
PORT = int(os.getenv("PORT", "10000"))  # Render assigns a PORT env automatically

# Admin IDs
DEFAULT_ADMIN_IDS = [1840751528, 1280460690, 1873662628]
ADMIN_IDS = list({
    *DEFAULT_ADMIN_IDS,
    *[int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
})

# Buttons/links
CHANNEL_BUTTON_TEXT = os.getenv("CHANNEL_BUTTON_TEXT", "NANAS44 OFFICIAL CHANNEL")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/nanas44")
GROUP_BUTTON_TEXT = os.getenv("GROUP_BUTTON_TEXT", "E-WALLET ANGPAO GROUP")
GROUP_URL = os.getenv("GROUP_URL", "https://t.me/addlist/OyQ3Pns_j3w5Y2M1")

WELCOME_IMAGE = os.getenv("WELCOME_IMAGE", "banner-01.png")
SUBSCRIBER_FILE = os.getenv("SUBSCRIBER_FILE", "subscribers.txt")
LOG_DIR = os.getenv("LOG_DIR", "logs")
DELAY = float(os.getenv("DELAY", "0.5"))  # seconds between messages

TZ = ZoneInfo(os.getenv("TZ", "Asia/Kuala_Lumpur"))

# ---------------------- Logging ----------------------
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "bot.log"), encoding="utf-8"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger("crown2u-bot")


def add_subscriber(chat_id: int) -> bool:
    """Add chat_id to subscribers file if not exists."""
    try:
        if not os.path.exists(SUBSCRIBER_FILE):
            with open(SUBSCRIBER_FILE, "w", encoding="utf-8") as f:
                f.write("")
        with open(SUBSCRIBER_FILE, "r", encoding="utf-8") as f:
            ids = {line.strip() for line in f if line.strip()}
        if str(chat_id) in ids:
            return False
        with open(SUBSCRIBER_FILE, "a", encoding="utf-8") as f:
            f.write(f"{chat_id}\n")
        return True
    except Exception as e:
        logger.exception("Failed to add subscriber: %s", e)
        return False


def load_subscribers() -> list[int]:
    try:
        if not os.path.exists(SUBSCRIBER_FILE):
            return []
        with open(SUBSCRIBER_FILE, "r", encoding="utf-8") as f:
            return [int(x.strip()) for x in f if x.strip().isdigit()]
    except Exception as e:
        logger.exception("Failed to load subscribers: %s", e)
        return []


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def build_welcome_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(CHANNEL_BUTTON_TEXT, url=CHANNEL_URL)],
        [InlineKeyboardButton(GROUP_BUTTON_TEXT, url=GROUP_URL)],
    ]
    return InlineKeyboardMarkup(buttons)


# ---------------------- Handlers ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    added = add_subscriber(chat.id)

    welcome_text = (
        f"👋 HI {user.first_name or 'there'}！\n\n"
        "🪜 Step 1:\nJoin Nanas44 Official Channel Claim Free 🎁\n\n"
        "🪜 Step 2:\nJoin Grouplink IOI Partnership Ambil E-wallet Angpaw 💸"
    )

    kb = build_welcome_kb()

    if os.path.exists(WELCOME_IMAGE):
        try:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=InputFile(WELCOME_IMAGE),
                caption=welcome_text,
                reply_markup=kb,
            )
        except Exception as e:
            logger.warning("Failed to send welcome image: %s", e)
            await context.bot.send_message(chat_id=chat.id, text=welcome_text, reply_markup=kb)
    else:
        await context.bot.send_message(chat_id=chat.id, text=welcome_text, reply_markup=kb)

    if added:
        logger.info("New subscriber added: %s", chat.id)


async def subcount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return
    subs = load_subscribers()
    await update.effective_message.reply_text(f"📈 Subscribers: {len(subs)}")


async def export_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return
    subs = load_subscribers()
    if not subs:
        await update.effective_message.reply_text("No subscribers yet.")
        return
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=InputFile(SUBSCRIBER_FILE),
        caption=f"Subscribers ({len(subs)})"
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    subs = load_subscribers()
    if not subs:
        await update.effective_message.reply_text("No subscribers to broadcast to.")
        return

    reply = update.effective_message.reply_to_message
    text = " ".join(context.args) if context.args else None

    sent = 0
    fail = 0
    for chat_id in subs:
        try:
            if reply:
                await reply.copy(chat_id)
            elif text:
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
            else:
                continue
            sent += 1
        except Exception as e:
            logger.warning("Broadcast to %s failed: %s", chat_id, e)
            fail += 1
        await asyncio.sleep(DELAY)

    await update.effective_message.reply_text(f"✅ Broadcast sent: {sent}, ❌ failed: {fail}")


async def forward_channel_to_subs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    forward_origin = getattr(msg, "forward_origin", None)
    if not forward_origin or not getattr(forward_origin, "chat", None):
        return

    origin_chat = forward_origin.chat
    origin_msg_id = forward_origin.message_id

    subs = load_subscribers()
    if not subs:
        return

    for chat_id in subs:
        try:
            await context.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=origin_chat.id,
                message_id=origin_msg_id,
            )
        except Exception as e:
            logger.warning("Copy to %s failed: %s", chat_id, e)
        await asyncio.sleep(DELAY)


async def daily_backup_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        subs = load_subscribers()
        caption = f"🗂️ Daily backup — subscribers ({len(subs)})"
        if os.path.exists(SUBSCRIBER_FILE):
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_document(
                        chat_id=admin_id,
                        document=InputFile(SUBSCRIBER_FILE),
                        caption=caption
                    )
                except Exception as e:
                    logger.warning("Backup to %s failed: %s", admin_id, e)
    except Exception as e:
        logger.exception("Daily backup job failed: %s", e)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update.effective_user.id):
        return
    txt = (
        "<b>Admin Commands</b>\n"
        "/subcount - Show subscriber count\n"
        "/export_subscribers - Send subscribers.txt\n"
        "/broadcast <text> or reply to a message with /broadcast\n\n"
        "<b>Forwarding</b>\n"
        "Forward any channel post to this bot to fanout to all subscribers."
    )
    await update.effective_message.reply_text(txt, parse_mode=ParseMode.HTML)


# ---------------------- Application / Webhook ----------------------
def build_app() -> Application:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("subcount", subcount))
    app.add_handler(CommandHandler("export_subscribers", export_subscribers))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.FORWARDED, forward_channel_to_subs))

    app.job_queue.run_daily(daily_backup_job, time=dtime(hour=0, minute=0, tzinfo=TZ))
    return app


async def main() -> None:
    if not BOT_TOKEN or not WEBHOOK_URL:
        raise RuntimeError("BOT_TOKEN and WEBHOOK_URL env vars are required.")

    application = build_app()
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)

    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="",
    )
    logger.info("Bot webhook running on port %s", PORT)
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
