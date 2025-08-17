import os
import zipfile
import rarfile
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"/tmp/{update.message.document.file_name}"
    await file.download_to_drive(file_path)

    first_image_path = "/tmp/first_page.jpg"

    if file_path.endswith(".cbz"):
        with zipfile.ZipFile(file_path, 'r') as archive:
            name = [n for n in archive.namelist() if n.lower().endswith((".jpg", ".jpeg", ".png"))][0]
            archive.extract(name, "/tmp")
            os.rename(f"/tmp/{name}", first_image_path)

    elif file_path.endswith(".cbr"):
        rarfile.UNRAR_TOOL = "unrar"  # o bsdtar en Render si no hay unrar
        with rarfile.RarFile(file_path) as archive:
            name = [n for n in archive.namelist() if n.lower().endswith((".jpg", ".jpeg", ".png"))][0]
            archive.extract(name, "/tmp")
            os.rename(f"/tmp/{name}", first_image_path)

    await update.message.reply_photo(photo=open(first_image_path, 'rb'))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        webhook_url=f"https://TU_APP.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()
