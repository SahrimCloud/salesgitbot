import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, 
    ContextTypes, ConversationHandler, CallbackContext
)
from aiohttp import web  # Librería adicional para el servidor web

# Estados de la conversación
NOMBRE, PETICION, CLIENTE, CANTIDAD, COLOR, DIMENSIONES, ENLACE, FECHA, COMENTARIOS, FOTOS, EDITAR = range(11)

# --- Conversación del bot (igual a tu código original) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()  
    await update.message.reply_text("Bienvenido. Por favor, ingresa el nombre de la persona o empresa:")
    return NOMBRE

# Funciones de conversación (mismas que en tu código)

async def cancelar(update: Update, context: CallbackContext):
    await update.message.reply_text("Solicitud cancelada. Puedes iniciar de nuevo con /start.")
    return ConversationHandler.END

# --- Nuevo: Manejador de ping ---
async def handle_ping(request):
    """Responde a los pings de UptimeRobot."""
    return web.Response(text="Bot activo", status=200)

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    # --- Conversación del bot ---
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre)],
            PETICION: [MessageHandler(filters.TEXT & ~filters.COMMAND, peticion)],
            CLIENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cliente)],
            CANTIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, cantidad)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color)],
            DIMENSIONES: [MessageHandler(filters.TEXT & ~filters.COMMAND, dimensiones)],
            ENLACE: [MessageHandler(filters.ALL & ~filters.COMMAND, enlace)],
            FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, fecha)],
            COMENTARIOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, comentarios)],
            FOTOS: [MessageHandler(filters.PHOTO, fotos), CommandHandler("skip", skip_fotos)],
            EDITAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, editar_campo)],
        },
        fallbacks=[CommandHandler("cancel", cancelar), CommandHandler("editar", editar)],
    )
    app.add_handler(conv_handler)

    # --- Nuevo: Servidor web para pings ---
    web_app = web.Application()
    web_app.router.add_get("/", handle_ping)

    # Correr el bot y el servidor web
    app.run_webhook(
        listen="0.0.0.0",  # Escucha en todas las interfaces
        port=int(os.getenv("PORT", 5000)),  # Puerto definido por Render
        webhook_url=os.getenv("RENDER_EXTERNAL_URL") + "/webhook",
    )

    web.run_app(web_app, port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    main()
