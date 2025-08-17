import os
import zipfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

TOKEN = os.getenv("BOT_TOKEN")

# --- Extraer primera imagen de CBZ ---
def extract_first_from_cbz(path, out_path):
    with zipfile.ZipFile(path, "r") as z:
        # Buscar imágenes dentro del CBZ
        imgs = sorted([f for f in z.namelist() if f.lower().endswith((".jpg", ".jpeg", ".png"))])
        if not imgs:
            return None
        with z.open(imgs[0]) as f:
            img = Image.open(f)
            img.save(out_path)
        return out_path

# --- Comando start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 Mándame un archivo .cbz y te muestro la primera página.")

# --- Manejar documentos ---
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        return

    file_path = await doc.get_file()
    local_path = f"/tmp/{doc.file_name}"
    await file_path.download_to_drive(local_path)

    out_path = "/tmp/first_page.jpg"
    result = None

    if local_path.lower().endswith(".cbz"):
        result = extract_first_from_cbz(local_path, out_path)

    if result:
        await update.message.reply_photo(photo=open(out_path, "rb"))
    else:
        await update.message.reply_text("❌ No encontré imágenes en ese .cbz.")

# --- Main ---
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Configurar Webhook en Render
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
