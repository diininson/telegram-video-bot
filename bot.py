import os
import logging
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp
from flask import Flask

# ==========================================
# PART 1: THE FAKE WEBSITE (To trick Render)
# ==========================================
app = Flask(__name__)


@app.route('/')
def health_check():
    return "Bot is alive and running!"


def run_web_server():
    # Render assigns a specific PORT (usually 10000). We must listen on it.
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


# ==========================================
# PART 2: THE BOT LOGIC
# ==========================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"User sent: {text}")

    if "http" in text:
        await update.message.reply_text("⏳ Downloading... please wait.")
        try:
            filename = download_video(text)
            await update.message.reply_text("📤 Uploading...")
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(filename, 'rb'))
            os.remove(filename)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    else:
        await update.message.reply_text("Send me a link!")


if __name__ == '__main__':
    # 1. Start the Fake Website in the background
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()

    # 2. Start the Bot
    # REPLACE WITH YOUR TOKEN
    TOKEN = "8504372333:AAHP7piO6pS3JXG7v7m0OGyWQQ64hwmzO4g"

    application = ApplicationBuilder().token(TOKEN).build()
    handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(handler)

    print("Bot is running...")
    application.run_polling()