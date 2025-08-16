import os
import zipfile
import rarfile
from PIL import Image
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")  # Lo pondrás en Render
URL = os.getenv("RENDER_EXTERNAL_URL")  # Render lo genera solo

def get_first_image(file_path):
    images = []

    if file_path.endswith(".cbz"):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            images = sorted([f for f in zip_ref.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            if images:
                with zip_ref.open(images[0]) as f:
                    return Image.open(f).convert("RGB")

    elif file_path.endswith(".cbr"):
        with rarfile.RarFile(file_path, "r") as rar_ref:
            images = sorted([f for f in rar_ref.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            if images:
                with rar_ref.open(images[0]) as f:
                    return Image.open(f).convert("RGB")

    return None

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"./{update.message.document.file_name}"
    await file.download_to_drive(file_path)

    img = get_first_image(file_path)
    if img:
        bio = BytesIO()
        bio.name = "first_page.jpg"
        img.save(bio, "JPEG")
        bio.seek(0)
        await update.message.reply_photo(photo=bio, caption="📖 Primera página del cómic")
    else:
        await update.message.reply_text("⚠️ No encontré imágenes en este archivo.")

    os.remove(file_path)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envíame un archivo .cbr o .cbz y te muestro la primera página 📚")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Webhook para Render
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TOKEN,
        webhook_url=f"{URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
