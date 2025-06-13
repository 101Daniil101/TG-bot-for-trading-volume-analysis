import logging
from datetime import datetime
from pathlib import Path
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)


from Scripts.user_func import (
    analys_based_on_trading_pair_timeframe_numbers_candles,
    analys_based_on_trading_pair_timeframe_start_end,
)

# Настройка логирования ошибок бота
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename='bot_errors.log'
)
logger = logging.getLogger(__name__)

# Состояния диалога
(
    SELECT_ANALYSIS_TYPE,  # Выбор типа анализа
    SELECT_TRADE_TYPE,     # Выбор типа контракта
    INPUT_TRADE_PAIR,      # Ввод торговой пары
    INPUT_TIMEFRAME,       # Выбор таймфрейма
    INPUT_CANDLES_COUNT,   # Ввод количества свечей
    INPUT_START_TIME,      # Ввод времени начала
    INPUT_END_TIME,        # Ввод времени окончания
) = range(7)

# Доступные таймфреймы (в минутах)
TIMEFRAMES = ["1", "3", "5", "15", "30", "60"]

# Клавиатура выбора типа анализа
analysis_keyboard = [
    [InlineKeyboardButton("Последние N свечей", callback_data="last_candles")],
    [InlineKeyboardButton("Диапазон времени", callback_data="time_range")]
]

# Клавиатура выбора типа контракта
trade_type_keyboard = [
    [InlineKeyboardButton("SPOT", callback_data="SPOT")],
    [InlineKeyboardButton("FUTURES", callback_data="FUTURES")],
    [InlineKeyboardButton("PERPETUAL FUTURES", callback_data="PERPETUAL FUTURES")]
]

# Клавиатура выбора таймфрейма (разбита на ряды по 2 кнопки)
timeframe_keyboard = [
    [InlineKeyboardButton(tf, callback_data=tf) for tf in TIMEFRAMES[i:i+2]] 
    for i in range(0, len(TIMEFRAMES), 2)
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start, инициализирует диалог анализа."""
    await update.message.reply_text(
        "Выберите тип анализа:",
        reply_markup=InlineKeyboardMarkup(analysis_keyboard))
    return SELECT_ANALYSIS_TYPE


async def select_analysis_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор типа анализа."""
    query = update.callback_query
    await query.answer()
    
    # Сохраняем выбранный тип анализа
    context.user_data["analysis_type"] = query.data
    
    await query.edit_message_text(
        text="Выберите тип контракта:",
        reply_markup=InlineKeyboardMarkup(trade_type_keyboard))
    return SELECT_TRADE_TYPE


async def select_trade_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор типа контракта."""
    query = update.callback_query
    await query.answer()
    
    trade_type = query.data
    context.user_data["trade_type"] = trade_type
    
    # Генерируем пример ввода для разных типов контрактов
    if trade_type == "SPOT":
        example = "BTC/USDT"
    elif trade_type == "FUTURES":
        example = "BTC/USDT-25DEC25"
    else:  # PERPETUAL FUTURES
        example = "BTC/USDT"
    
    await query.edit_message_text(
        text=f"Введите торговую пару ({trade_type}):\nПример: {example}")
    return INPUT_TRADE_PAIR


async def input_trade_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Валидирует и сохраняет торговую пару."""
    trade_pair = update.message.text.strip().upper()
    trade_type = context.user_data["trade_type"]
    
    # Проверка формата пары
    if "/" not in trade_pair:
        await update.message.reply_text(
            "❌ Неверный формат. Используйте / для разделения пар. Попробуйте еще раз:")
        return INPUT_TRADE_PAIR
    
    # Проверка специфики формата для разных типов контрактов
    base, quote = trade_pair.split("/", 1)
    if trade_type == "FUTURES" and "-" not in quote:
        await update.message.reply_text(
            "❌ Для FUTURES укажите дату экспирации (например BTC/USDT-25DEC25):")
        return INPUT_TRADE_PAIR
    elif trade_type != "FUTURES" and "-" in quote:
        await update.message.reply_text(
            "❌ Для SPOT/PERPETUAL не указывайте дату. Попробуйте еще раз:")
        return INPUT_TRADE_PAIR
    
    context.user_data["trade_pair"] = trade_pair
    
    # Запрос таймфрейма
    await update.message.reply_text(
        "Выберите таймфрейм:",
        reply_markup=InlineKeyboardMarkup(timeframe_keyboard))
    return INPUT_TIMEFRAME


async def input_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор таймфрейма и запрашивает следующие данные."""
    query = update.callback_query
    await query.answer()
    
    context.user_data["timeframe"] = query.data
    
    # Ветвление по типу анализа
    if context.user_data["analysis_type"] == "last_candles":
        await query.edit_message_text(text="Введите количество свечей (1-1000):")
        return INPUT_CANDLES_COUNT
    else:
        await query.edit_message_text(text="Введите время начала (ДД.ММ.ГГГГ ЧЧ:ММ):")
        return INPUT_START_TIME


async def input_candles_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Валидирует и сохраняет количество свечей."""
    try:
        count = int(update.message.text.strip())
        if not 1 <= count <= 1000:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введите число от 1 до 1000:")
        return INPUT_CANDLES_COUNT
    
    context.user_data["candles_count"] = count
    await run_analysis(update, context)
    return ConversationHandler.END


async def input_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Валидирует и сохраняет время начала."""
    try:
        datetime.strptime(update.message.text.strip(), "%d.%m.%Y %H:%M")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат. Используйте ДД.ММ.ГГГГ ЧЧ:ММ:")
        return INPUT_START_TIME
    
    context.user_data["start_time"] = update.message.text.strip()
    await update.message.reply_text("Введите время окончания (ДД.ММ.ГГГГ ЧЧ:ММ):")
    return INPUT_END_TIME


async def input_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Валидирует время окончания и запускает анализ."""
    try:
        end = datetime.strptime(update.message.text.strip(), "%d.%m.%Y %H:%M")
        start = datetime.strptime(context.user_data["start_time"], "%d.%m.%Y %H:%M")
        if end <= start:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "❌ Время окончания должно быть позже начала. Попробуйте еще раз:")
        return INPUT_END_TIME
    
    context.user_data["end_time"] = update.message.text.strip()
    await run_analysis(update, context)
    return ConversationHandler.END


async def run_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает анализ и отправляет результаты пользователю."""
    user_data = context.user_data
    chat_id = update.effective_chat.id
    
    try:
        # Уведомление о начале обработки
        await context.bot.send_message(chat_id, "⏳ Запрашиваю данные с бирж...")
        
        # Выбор функции анализа по типу
        if user_data["analysis_type"] == "last_candles":
            result = analys_based_on_trading_pair_timeframe_numbers_candles(
                user_data["trade_pair"],
                user_data["trade_type"],
                user_data["timeframe"],
                str(user_data["candles_count"]))
        else:
            result = analys_based_on_trading_pair_timeframe_start_end(
                user_data["trade_pair"],
                user_data["trade_type"],
                user_data["timeframe"],
                user_data["start_time"],
                user_data["end_time"])
        
        # Проверка наличия результатов
        if not result:
            raise ValueError("Нет данных для отображения")
        
        # Подписи к графикам
        captions = {
            "volume_plot.png": "📊 Сравнение объемов",
            "obv_plot.png": "📈 Индикатор OBV", 
            "vwap_comparison.png": "📉 Сравнение VWAP",
            "volume_pie_BTC-USDT.png": "🔢 Распределение объемов",
            "volume_profile_comparison.png": "📌 Объемный профиль"
        }
        
        # Отправка графиков
        for img in result:
            if img and Path(img).exists():
                with open(img, 'rb') as photo:
                    caption = captions.get(Path(img).name, "Результат анализа")
                    await context.bot.send_photo(chat_id, photo, caption=caption)
        
        # Финальное сообщение с параметрами анализа
        await context.bot.send_message(
            chat_id,
            f"✅ Анализ завершен!\n"
            f"Пара: {user_data['trade_pair']}\n" 
            f"Тип: {user_data['trade_type']}\n"
            f"Таймфрейм: {user_data['timeframe']}m"
        )
    
    except Exception as e:
        # Обработка различных ошибок
        error_msg = "❌ Ошибка анализа: "
        if "не существует" in str(e):
            error_msg += "неверная торговая пара"
        elif "Cannot cut empty array" in str(e):
            error_msg += "нет данных для указанного периода"
        else:
            error_msg += str(e)
        
        await context.bot.send_message(chat_id, error_msg)
        logger.error(f"Analysis error: {str(e)}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет текущую операцию."""
    await update.message.reply_text("Операция отменена. Для нового анализа /start")
    return ConversationHandler.END


def main():
    """Основная функция инициализации и запуска бота."""
    # Инициализация приложения бота

    # Определяем путь к config.json (по умолчанию в корне проекта)
    config_path = Path("config.json")
    
    if not config_path.exists():
        raise FileNotFoundError(f"Файл {config_path} не найден")

    # Читаем токен из JSON
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    bot_token = config.get("BOT_TOKEN")
    if not bot_token:
        raise ValueError("Токен бота BOT_TOKEN не найден в config.json")

    # Инициализация приложения бота
    app = ApplicationBuilder().token(bot_token).build()
    
    # Настройка обработчика диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_ANALYSIS_TYPE: [CallbackQueryHandler(select_analysis_type)],
            SELECT_TRADE_TYPE: [CallbackQueryHandler(select_trade_type)],
            INPUT_TRADE_PAIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_trade_pair)],
            INPUT_TIMEFRAME: [CallbackQueryHandler(input_timeframe)],
            INPUT_CANDLES_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_candles_count)],
            INPUT_START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_start_time)],
            INPUT_END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_end_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Регистрация обработчика и запуск бота
    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
