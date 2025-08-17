import rarfile
import io
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = 8299997511:AAGlB2LoP-p0RS06M7ZtMTt0OVlvnxUNXtE

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Envía un archivo .cbr para obtener la primera página!")

async def handle_cbr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_bytes = await file.download_as_bytearray()

    try:
        with rarfile.RarFile(io.BytesIO(file_bytes)) as r:
            first_img_name = sorted(r.namelist())[0]
            img_data = r.read(first_img_name)
            await update.message.reply_photo(photo=img_data)
    except rarfile.RarCannotExec:
        await update.message.reply_text(
            "No se puede abrir el CBR: falta unrar en el servidor."
        )
    except Exception as e:
        await update.message.reply_text(f"Error al procesar el CBR: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.FileExtension("cbr"), handle_cbr))

app.run_polling()
