
import logging
import os

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "📸 Send only a photo.\n"
        "Your photo will be posted anonymously in the group."
    )


async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.message

    try:
        await context.bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )

        await message.reply_text(
            "✅ Your photo was posted anonymously!"
        )

    except TelegramError:
        logger.exception("Photo posting failed")

        await message.reply_text(
            "❌ Sorry, photo could not be posted."
        )


async def reject_other_messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📸 Please send photos only!"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.PHOTO,
            photo_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND,
            reject_other_messages
        )
    )

    logger.info("Photo-only anonymous bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
    
