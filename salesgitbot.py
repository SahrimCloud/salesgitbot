import os
import asyncio  # Necesario para manejar tareas asíncronas
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, 
    ContextTypes, ConversationHandler, CallbackContext
)
from aiohttp import web, ClientSession  # Para el servidor web y hacer pings HTTP

# Estados de la conversación
NOMBRE, PETICION, CLIENTE, CANTIDAD, COLOR, DIMENSIONES, ENLACE, FECHA, COMENTARIOS, FOTOS, EDITAR = range(11)

# --- Conversación del bot ---
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
    """Responde a los pings de prueba."""
    return web.Response(text="Bot activo", status=200)

# --- Nuevo: Tarea de auto-ping ---
async def auto_ping():
    """Envía pings cada minuto para mantener la aplicación activa."""
    url = os.getenv("RENDER_EXTERNAL_URL")  # URL de tu app en Render
    async with ClientSession() as session:
        while True:
            try:
                async with session.get(url) as response:
                    print(f"Ping enviado. Estado: {response.status}")
            except Exception as e:
                print(f"Error en el ping: {e}")
            await asyncio.sleep(60)  # Espera 60 segundos antes de enviar otro ping

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

    # --- Servidor web para pings ---
    web_app = web.Application()
    web_app.router.add_get("/", handle_ping)

    # Ejecutar el servidor web en un puerto específico
    loop = asyncio.get_event_loop()
    loop.create_task(auto_ping())  # Lanzar la tarea de auto-ping en paralelo

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        webhook_url=os.getenv("RENDER_EXTERNAL_URL") + "/webhook",
    )

    web.run_app(web_app, port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    main()
