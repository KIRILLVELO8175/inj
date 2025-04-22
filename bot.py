import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, ContextTypes

ORDER_NUMBER, RETURN_DATETIME, PHOTO = range(3)

ADMIN_USERNAMES = ["T_Kiro", "greaats28", "hermaeus_mora7", "Artemkkkkks"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Лобач. Скинь мне номер заказа и я все сделаю красиво")
    return ORDER_NUMBER

async def order_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order_number'] = update.message.text
    await update.message.reply_text("Введи число и время того, когда ты закинул пакет обратно на склад на ячейку возврата")
    return RETURN_DATETIME

async def return_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['return_datetime'] = update.message.text
    await update.message.reply_text("Загрузи фото возвращенного заказа и предупреди логиста")
    return PHOTO

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    context.user_data['photo'] = photo

    # Ответ пользователю
    await update.message.reply_text("Заявка отправлена на подтверждение")

    # Кнопки
    keyboard = [
        [
            InlineKeyboardButton("Подтвердить", callback_data='approve'),
            InlineKeyboardButton("Отклонить", callback_data='reject'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"Новая заявка:\n"
        f"Номер заказа: {context.user_data['order_number']}\n"
        f"Дата и время возврата: {context.user_data['return_datetime']}"
    )

    # Отправка всем администраторам
    for admin in ADMIN_USERNAMES:
        try:
            await context.bot.send_photo(
                chat_id=f"@{admin}",
                photo=photo,
                caption=text,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Ошибка при отправке админу {admin}: {e}")

    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'approve':
        await query.edit_message_caption(caption="Заявка подтверждена.")
    else:
        await query.edit_message_caption(caption="Заявка отклонена.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

def main():
    token = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ORDER_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_number)],
            RETURN_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, return_datetime)],
            PHOTO: [MessageHandler(filters.PHOTO, photo_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


    main()
