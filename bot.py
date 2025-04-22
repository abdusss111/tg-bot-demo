from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from config import TOKEN, NAME

# Состояния диалога
(
    ASK_NAME, ASK_LEVEL, ASK_FORMAT, ASK_MODE, ASK_SCHEDULE,
    SUGGEST_TRIAL, CONFIRM_TRIAL
) = range(7)

user_data = {}

# Приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Здравствуйте! Вас приветствует школа английского языка {NAME}.\n"
        f"Чем могу помочь?"
    )
    return ASK_NAME

# Сбор имени
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Подскажите, пожалуйста, как вас зовут?")
    return ASK_LEVEL

# Сбор уровня
async def ask_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["client_name"] = update.message.text
    await update.message.reply_text(
        "Для какого уровня вы ищете занятия? (Начальный, средний, продвинутый)"
    )
    return ASK_FORMAT

# Индивидуально или в группе
async def ask_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["level"] = update.message.text
    await update.message.reply_text("Интересуетесь индивидуальными или групповыми уроками?")
    return ASK_MODE

# Онлайн или офлайн
async def ask_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["format"] = update.message.text
    await update.message.reply_text("В каком формате вам удобнее заниматься — онлайн или офлайн?")
    return ASK_SCHEDULE

# Удобное расписание
async def ask_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = update.message.text
    await update.message.reply_text("В какие дни и время вам удобно?")
    return SUGGEST_TRIAL

# Предложение времени
async def suggest_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["schedule"] = update.message.text

    # Здесь можно подключить базу или API для реальных слотов
    trial_date = "пятница, 26 апреля"
    trial_time = "15:00"
    teacher = "Анна"

    context.user_data["trial_info"] = f"{trial_date} в {trial_time} с преподавателем {teacher}"

    await update.message.reply_text(
        f"Спасибо за информацию!\n"
        f"Мы можем предложить вам пробный урок {context.user_data['trial_info']}.\n"
        f"Подходит ли вам это время?"
    )
    return CONFIRM_TRIAL

# Подтверждение
async def confirm_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text.lower()
    if "да" in answer or "подходит" in answer:
        info = context.user_data["trial_info"]
        mode = context.user_data["mode"].lower()

        place = (
            "в Zoom. Мы пришлем вам ссылку за день до урока."
            if "онлайн" in mode else
            "в нашем офисе по адресу: ул. Абая, 25. Мы напомним за день до урока."
        )

        await update.message.reply_text(
            f"Отлично, записала вас на пробный урок {info}.\nУрок пройдет {place}"
        )
        await update.message.reply_text(
            "Спасибо за запись! Если возникнут вопросы — пишите в любое время.\nДо встречи на занятии!"
        )
    else:
        await update.message.reply_text("Хорошо, можем подобрать другое время. Напишите, когда удобно.")
        return ASK_SCHEDULE

    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо, если что — пишите!")
    return ConversationHandler.END

# Запуск бота
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_level)],
            ASK_FORMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_format)],
            ASK_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_mode)],
            ASK_SCHEDULE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_schedule)],
            SUGGEST_TRIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, suggest_trial)],
            CONFIRM_TRIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_trial)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
