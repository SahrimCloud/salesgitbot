import os
from telegram import Update, ForceReply
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, 
    ConversationHandler, CallbackContext
)

# Estados de la conversación
NOMBRE, PETICION, CLIENTE, CANTIDAD, COLOR, DIMENSIONES, ENLACE, FECHA, COMENTARIOS, FOTOS = range(10)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia la conversación."""
    await update.message.reply_text("Bienvenido. Por favor, ingresa el nombre de la persona o empresa:")
    return NOMBRE

async def nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el nombre e inicia la siguiente pregunta."""
    context.user_data["nombre"] = update.message.text
    await update.message.reply_text("¿Cuál es el nombre de la petición?")
    return PETICION

async def peticion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda la petición y pregunta el tipo de cliente."""
    context.user_data["peticion"] = update.message.text
    await update.message.reply_text("¿Qué tipo de cliente es? Elige entre: Cosplayer, Premium o Nuevo.")
    return CLIENTE

async def cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el tipo de cliente."""
    tipo = update.message.text.lower()
    if tipo not in ["cosplayer", "premium", "nuevo"]:
        await update.message.reply_text("Por favor, elige: Cosplayer, Premium o Nuevo.")
        return CLIENTE
    context.user_data["cliente"] = tipo
    await update.message.reply_text("¿Cuál es la cantidad?")
    return CANTIDAD

async def cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cantidad"] = update.message.text
    await update.message.reply_text("¿De qué color es la pieza?")
    return COLOR

async def color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["color"] = update.message.text
    await update.message.reply_text("¿Cuáles son las dimensiones de la pieza?")
    return DIMENSIONES

async def dimensiones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["dimensiones"] = update.message.text
    await update.message.reply_text("Por favor, proporciona el enlace del STL o adjunta el archivo.")
    return ENLACE

async def enlace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        context.user_data["enlace"] = update.message.document.file_id
    else:
        context.user_data["enlace"] = update.message.text
    await update.message.reply_text("¿Cuál es la fecha de entrega?")
    return FECHA

async def fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fecha"] = update.message.text
    await update.message.reply_text("¿Deseas añadir algún comentario adicional?")
    return COMENTARIOS

async def comentarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comentarios"] = update.message.text
    await update.message.reply_text("Si quieres, adjunta fotos. Si no, escribe /skip.")
    return FOTOS

async def fotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["fotos"] = update.message.photo[-1].file_id
    await finalizar(update, context)
    return ConversationHandler.END

async def skip_fotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await finalizar(update, context)
    return ConversationHandler.END

async def finalizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el resumen de la solicitud."""
    data = context.user_data
    resumen = (
        f"✨ *Solicitud Completada* ✨\n\n"
        f"👤 *Nombre:* {data['nombre']}\n"
        f"📝 *Petición:* {data['peticion']}\n"
        f"🏷️ *Tipo de Cliente:* {data['cliente'].capitalize()}\n"
        f"🔢 *Cantidad:* {data['cantidad']}\n"
        f"🎨 *Color:* {data['color']}\n"
        f"📐 *Dimensiones:* {data['dimensiones']}\n"
        f"🔗 *Enlace/Archivo:* {data['enlace']}\n"
        f"📅 *Fecha de Entrega:* {data['fecha']}\n"
        f"💬 *Comentarios:* {data['comentarios']}\n"
        f"🖼️ *Fotos adjuntas:* {'Sí' if 'fotos' in data else 'No'}"
    )
    await update.message.reply_text(resumen, parse_mode="Markdown")

async def cancelar(update: Update, context: CallbackContext):
    """Cancela la conversación."""
    await update.message.reply_text("Solicitud cancelada. Puedes iniciar de nuevo con /start.")
    return ConversationHandler.END

def main():
    """Inicia el bot."""
    TOKEN = os.getenv("7404262192:AAE4s5O9Ob0RjwVCxfZlzDvkJkrbOSJRXVc")

    if not TOKEN:
        raise ValueError("No se encontró el token. Verifica las variables de entorno.")

    print(f"Usando el token: {TOKEN[:5]}... (truncado para seguridad)")

    app = ApplicationBuilder().token(TOKEN).build()

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
            FOTOS: [
                MessageHandler(filters.PHOTO, fotos),
                CommandHandler("skip", skip_fotos),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancelar)],
    )

    app.add_handler(conv_handler)

    print("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
