
import logging
import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("pending_photo", None)

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "📸 Upload your photo.\n"
        "Then press the Post Here button to share it anonymously."
    )


async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.message

    context.user_data["pending_photo"] = message.message_id

    keyboard = [
        [
            InlineKeyboardButton(
                "📤 Post Here",
                callback_data="post_photo"
            )
        ]
    ]

    await message.reply_text(
        "📸 Photo received!\n\n"
        "Press below to post it anonymously.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def post_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    photo_id = context.user_data.get("pending_photo")

    if not photo_id:
        await query.edit_message_text(
            "❌ No pending photo. Please upload again."
        )
        return

    try:
        await context.bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=query.message.chat_id,
            message_id=photo_id,
        )

        context.user_data.pop("pending_photo", None)

        await query.edit_message_text(
            "✅ Your photo was posted anonymously!"
        )

    except TelegramError:
        logger.exception("Failed to post photo")

        await query.edit_message_text(
            "❌ Could not post your photo. Please try again."
        )


async def reject_other_messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📸 Photos only, please!"
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
        CallbackQueryHandler(
            post_photo,
            pattern="^post_photo$"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND,
            reject_other_messages
        )
    )

    logger.info("Anonymous photo bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()
    
