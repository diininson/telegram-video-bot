import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

# 1. Setup logging (so we can see what's happening)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 2. The function that downloads the video
def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',     # Get best MP4 quality
        'outtmpl': '%(title)s.%(ext)s', # Name the file by its title
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# 3. The function that replies to messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"User sent: {text}") # Show in your terminal what user sent

    if "http" in text:
        await update.message.reply_text("⏳ Downloading... please wait.")
        
        try:
            # Download
            filename = download_video(text)
            print(f"Downloaded: {filename}")
            
            # Send to Telegram
            await update.message.reply_text("📤 Uploading...")
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(filename, 'rb'))
            
            # Cleanup (Delete file from computer)
            os.remove(filename)
            print("File sent and deleted.")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
            print(f"Error: {e}")
    else:
        await update.message.reply_text("Send me a link from Instagram, TikTok, or YouTube!")

# 4. Start the Bot
if __name__ == '__main__':
    # REPLACE THE TEXT BELOW WITH YOUR ACTUAL TOKEN
    TOKEN = "8504372333:AAHP7piO6pS3JXG7v7m0OGyWQQ64hwmzO4g"
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Listen for text messages
    handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(handler)
    
    print("Bot is running... (Press Ctrl+C to stop)")
    application.run_polling()