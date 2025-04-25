from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, filters
)
from handlers import (
    start, choose_role, advertiser_brand, advertiser_niche,
    advertiser_budget, advertiser_audience,
    save_blogger_name, save_blogger_links, save_blogger_topic,
    save_blogger_reach, save_blogger_price, finish_blogger,
    cancel, handle_show_bloggers
)

import os

TOKEN = '8085879338:AAHiW4fMyFffYE4hqY9rTTnRH2lQKmauMd8'  # Сюда вставьте свой токен

# Состояния
CHOOSING, ADVERTISER_BRAND, ADVERTISER_NICHE, ADVERTISER_BUDGET, ADVERTISER_AUDIENCE = range(5)
BLOGGER_NAME, BLOGGER_LINKS,BLOGGER_CATEGORIES, BLOGGER_TOPIC, BLOGGER_REACH, BLOGGER_PRICE = range(5, 11)

# Настройка бота
app = ApplicationBuilder().token(TOKEN).build()

# Определение обработчиков
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_role)],
        ADVERTISER_BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, advertiser_brand)],
        ADVERTISER_NICHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, advertiser_niche)],
        ADVERTISER_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, advertiser_budget)],
        ADVERTISER_AUDIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, advertiser_audience)],
        BLOGGER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_blogger_name)],
        BLOGGER_LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_blogger_links)],
        BLOGGER_CATEGORIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_blogger_topic)],
        BLOGGER_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_blogger_topic)],
        BLOGGER_REACH: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_blogger_reach)],
        BLOGGER_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_blogger_price)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# Команда для просмотра блогеров
app.add_handler(CommandHandler("bloggers", handle_show_bloggers))

# Добавляем обработчики
app.add_handler(conv_handler)

# Запуск бота
if __name__ == "__main__":
    print("✅ Бот запущен. Жди сообщений в Telegram...")
    app.run_polling()
