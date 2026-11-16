import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Anonymous posting bot. Text, photo, video edhu anuppunaalum group-la anonymous-ah post aagum."
    )


async def forward_anonymously(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg is None or msg.chat.type != "private":
        return
    try:
        await context.bot.copy_message(
            chat_id=GROUP_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id,
        )
        await msg.reply_text("Posted anonymously ✅")
    except Exception as e:
        logging.error(e)
        await msg.reply_text("Post panna mudiyala.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, forward_anonymously)
    )
    app.run_polling()


if __name__ == "__main__":
    main()
