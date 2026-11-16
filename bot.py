import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Configuration
BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Send me a text, photo, video, document or voice message.\n"
        "Your message will be posted anonymously in the group."
    )


async def forward_anonymously(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message is None:
        return

    try:
        if message.photo:
            photo_id = message.photo[-1].file_id
            bot_info = await context.bot.get_me()
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Post Here", url=f"https://t.me/{bot_info.username}"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_photo(
                chat_id=GROUP_ID,
                photo=photo_id,
                caption=message.caption,
                reply_markup=reply_markup,
            )
        else:
            await context.bot.copy_message(
                chat_id=GROUP_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )

        await message.reply_text("✅ Your message was posted anonymously!")

    except TelegramError:
        logger.exception("Failed to post message")
        await message.reply_text(" not be posted.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND,
            forward_anonymously,
        )
    )

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
