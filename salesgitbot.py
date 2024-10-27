from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, 
                          ConversationHandler, CallbackContext, CallbackQueryHandler)

# Etapas del flujo de la conversación
NOMBRE, PETICION, TIPO, CANTIDAD, COLOR, DIMENSIONES, ENLACE, FECHA, COMENTARIOS, FOTOS = range(10)

# Token del bot proporcionado por BotFather
TOKEN = "7404262192:AAE-Vhp4xBKbJF4xnUXl15Bw2svfeVlnSZo"

def start(update: Update, context: CallbackContext) -> int:
    """Inicia el proceso de solicitud."""
    update.message.reply_text('¡Hola! Empecemos con tu solicitud. Por favor ingresa tu **nombre o el de tu empresa**:')
    return NOMBRE

def nombre(update: Update, context: CallbackContext) -> int:
    context.user_data['nombre'] = update.message.text
    update.message.reply_text('¿Cuál es el **nombre de la petición**?')
    return PETICION

def peticion(update: Update, context: CallbackContext) -> int:
    context.user_data['peticion'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Cosplayer", callback_data='Cosplayer')],
        [InlineKeyboardButton("Premium", callback_data='Premium')],
        [InlineKeyboardButton("Nuevo", callback_data='Nuevo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Selecciona el **tipo de cliente**:', reply_markup=reply_markup)
    return TIPO

def tipo(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data['tipo'] = query.data
    query.edit_message_text(f"Seleccionaste: {query.data}. ¿Cuál es la **cantidad** solicitada?")
    return CANTIDAD

def cantidad(update: Update, context: CallbackContext) -> int:
    context.user_data['cantidad'] = update.message.text
    update.message.reply_text('¿Cuál es el **color** de la pieza?')
    return COLOR

def color(update: Update, context: CallbackContext) -> int:
    context.user_data['color'] = update.message.text
    update.message.reply_text('¿Cuáles son las **dimensiones** de la pieza? (Ej: 10x10x15 cm)')
    return DIMENSIONES

def dimensiones(update: Update, context: CallbackContext) -> int:
    context.user_data['dimensiones'] = update.message.text
    update.message.reply_text('Proporciona un **enlace al archivo STL** o **adjunta el archivo**.')
    return ENLACE

def enlace(update: Update, context: CallbackContext) -> int:
    if update.message.document:
        context.user_data['enlace'] = "Archivo adjunto."
    else:
        context.user_data['enlace'] = update.message.text
    update.message.reply_text('¿Cuál es la **fecha de entrega** esperada? (Ej: 2024-10-30)')
    return FECHA

def fecha(update: Update, context: CallbackContext) -> int:
    context.user_data['fecha'] = update.message.text
    update.message.reply_text('¿Tienes algún **comentario adicional**?')
    return COMENTARIOS

def comentarios(update: Update, context: CallbackContext) -> int:
    context.user_data['comentarios'] = update.message.text
    update.message.reply_text('Si deseas, puedes **adjuntar fotos de ejemplo**. De lo contrario, escribe /skip.')
    return FOTOS

def fotos(update: Update, context: CallbackContext) -> int:
    if update.message.photo:
        context.user_data['fotos'] = "Fotos adjuntadas."
    else:
        context.user_data['fotos'] = "Sin fotos."

    # Mostrar resumen de la solicitud
    resumen = (
        f"**Solicitud creada:**\n"
        f"Nombre: {context.user_data['nombre']}\n"
        f"Petición: {context.user_data['peticion']}\n"
        f"Tipo de cliente: {context.user_data['tipo']}\n"
        f"Cantidad: {context.user_data['cantidad']}\n"
        f"Color: {context.user_data['color']}\n"
        f"Dimensiones: {context.user_data['dimensiones']}\n"
        f"Enlace/Archivo: {context.user_data['enlace']}\n"
        f"Fecha de Entrega: {context.user_data['fecha']}\n"
        f"Comentarios: {context.user_data['comentarios']}\n"
        f"Fotos: {context.user_data['fotos']}"
    )
    update.message.reply_text(resumen, parse_mode='Markdown')
    return ConversationHandler.END

def skip_fotos(update: Update, context: CallbackContext) -> int:
    context.user_data['fotos'] = "Sin fotos."
    return fotos(update, context)

def cancelar(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Solicitud cancelada. ¡Hasta luego!')
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Definir el flujo de la conversación
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NOMBRE: [MessageHandler(Filters.text & ~Filters.command, nombre)],
            PETICION: [MessageHandler(Filters.text & ~Filters.command, peticion)],
            TIPO: [CallbackQueryHandler(tipo)],
            CANTIDAD: [MessageHandler(Filters.text & ~Filters.command, cantidad)],
            COLOR: [MessageHandler(Filters.text & ~Filters.command, color)],
            DIMENSIONES: [MessageHandler(Filters.text & ~Filters.command, dimensiones)],
            ENLACE: [MessageHandler(Filters.text | Filters.document, enlace)],
            FECHA: [MessageHandler(Filters.text & ~Filters.command, fecha)],
            COMENTARIOS: [MessageHandler(Filters.text & ~Filters.command, comentarios)],
            FOTOS: [
                MessageHandler(Filters.photo, fotos),
                CommandHandler('skip', skip_fotos)
            ],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )

    dp.add_handler(conv_handler)

    # Iniciar el bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
