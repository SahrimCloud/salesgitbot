import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, 
    ContextTypes, ConversationHandler, CallbackContext
)

# Estados de la conversación
NOMBRE, PETICION, CLIENTE, CANTIDAD, COLOR, DIMENSIONES, ENLACE, FECHA, COMENTARIOS, FOTOS, EDITAR = range(11)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia la conversación."""
    context.user_data.clear()  # Limpiar datos previos
    await update.message.reply_text("Bienvenido. Por favor, ingresa el nombre de la persona o empresa:")
    return NOMBRE

def generar_resumen_parcial(context):
    """Genera un resumen parcial de los datos ingresados."""
    data = context.user_data
    resumen = (
        f"👤 *Nombre*: {data.get('nombre', '-')}\n"
        f"📝 *Petición*: {data.get('peticion', '-')}\n"
        f"🏷️ *Cliente*: {data.get('cliente', '-').capitalize()}\n"
        f"🔢 *Cantidad*: {data.get('cantidad', '-')}\n"
        f"🎨 *Color*: {data.get('color', '-')}\n"
        f"📐 *Dimensiones*: {data.get('dimensiones', '-')}\n"
        f"🔗 *Enlace*: {data.get('enlace', '-')}\n"
        f"📅 *Fecha*: {data.get('fecha', '-')}\n"
        f"💬 *Comentarios*: {data.get('comentarios', '-')}\n"
        f"🖼️ *Fotos*: {'Sí' if 'fotos' in data else 'No'}\n"
    )
    return resumen

async def mostrar_resumen_parcial(update, context):
    """Muestra los datos parciales cada vez que se añade información."""
    resumen = generar_resumen_parcial(context)
    await update.message.reply_text(f"📋 Resumen Parcial:\n{resumen}", parse_mode="Markdown")

async def nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nombre"] = update.message.text
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("¿Cuál es el nombre de la petición?")
    return PETICION

async def peticion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["peticion"] = update.message.text
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("¿Qué tipo de cliente es? Elige entre: Cosplayer, Premium o Nuevo.")
    return CLIENTE

async def cliente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tipo = update.message.text.lower()
    if tipo not in ["cosplayer", "premium", "nuevo"]:
        await update.message.reply_text("Por favor, elige: Cosplayer, Premium o Nuevo.")
        return CLIENTE
    context.user_data["cliente"] = tipo
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("¿Cuál es la cantidad?")
    return CANTIDAD

async def cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cantidad"] = update.message.text
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("¿De qué color es la pieza?")
    return COLOR

async def color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["color"] = update.message.text
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("¿Cuáles son las dimensiones de la pieza?")
    return DIMENSIONES

async def dimensiones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["dimensiones"] = update.message.text
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("Por favor, proporciona el enlace del STL o adjunta el archivo.")
    return ENLACE

async def enlace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        context.user_data["enlace"] = update.message.document.file_id
    else:
        context.user_data["enlace"] = update.message.text
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("¿Cuál es la fecha de entrega?")
    return FECHA

async def fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fecha"] = update.message.text
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("¿Deseas añadir algún comentario adicional?")
    return COMENTARIOS

async def comentarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comentarios"] = update.message.text
    await mostrar_resumen_parcial(update, context)
    await update.message.reply_text("Si quieres, adjunta fotos. Si no, escribe /skip.")
    return FOTOS

async def fotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["fotos"] = update.message.photo[-1].file_id
    await mostrar_resumen(update, context)
    return ConversationHandler.END

async def skip_fotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_resumen(update, context)
    return ConversationHandler.END

async def mostrar_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el resumen completo de la solicitud."""
    resumen = generar_resumen_parcial(context)

    await update.message.reply_text(f"✨ *Solicitud Completada* ✨\n\n{resumen}", parse_mode="Markdown")

    if "enlace" in context.user_data:
        if context.user_data["enlace"].startswith("http"):
            await update.message.reply_text(
                f"🔗 [Ver Enlace]({context.user_data['enlace']})", parse_mode="Markdown"
            )
        else:
            await update.message.reply_document(context.user_data["enlace"])

    if "fotos" in context.user_data:
        await update.message.reply_photo(context.user_data["fotos"], caption="📸 Vista previa de la foto.")

    await update.message.reply_text("Si deseas modificar algo, usa /editar. Para finalizar, usa /cancel.")

async def editar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [["Nombre", "Petición", "Cliente"], ["Cantidad", "Color", "Dimensiones"], 
               ["Enlace", "Fecha", "Comentarios"]]
    markup = ReplyKeyboardMarkup(teclado, one_time_keyboard=True)
    await update.message.reply_text("¿Qué deseas editar?", reply_markup=markup)
    return EDITAR

async def editar_campo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    campo = update.message.text.lower()
    if campo in context.user_data:
        await update.message.reply_text(f"Ingrese el nuevo valor para {campo}:")
        return globals()[campo.upper()]
    else:
        await update.message.reply_text("Campo inválido. Intenta nuevamente.")
        return EDITAR

async def cancelar(update: Update, context: CallbackContext):
    await update.message.reply_text("Solicitud cancelada. Puedes iniciar de nuevo con /start.")
    return ConversationHandler.END

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
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
            FOTOS: [MessageHandler(filters.PHOTO, fotos), CommandHandler("skip", skip_fotos)],
            EDITAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, editar_campo)],
        },
        fallbacks=[CommandHandler("cancel", cancelar), CommandHandler("editar", editar)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
