from telegram import Update, ReplyKeyboardMarkup 
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

TOKEN = '8085879338:AAHiW4fMyFffYE4hqY9rTTnRH2lQKmauMd8'  # Вставь свой токен

ADMIN_CHAT_ID = 235130655

CHOOSING, ADVERTISER, BLOGGER = range(3)

# === Авторизация через сервисный аккаунт для Google Sheets ===
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Telegram bot\telegram-bot-457614-0096237ea079.json", scope)
    client = gspread.authorize(creds)
    return client

import os

if not os.path.exists(r"C:\Telegram bot\telegram-bot-457614-0096237ea079.json"):
    print("⚠️ Файл JSON не найден! Проверь имя или путь.")
    exit()

# Открываем таблицу по названию
def open_google_sheet():
    client = authenticate_google_sheets()
    sheet = client.open("Заявки Telegram").sheet1  # Укажи имя своей таблицы
    return sheet

# Функция для добавления новой строки в таблицу
def add_to_google_sheet(data):
    sheet = open_google_sheet()
    sheet.append_row(data)

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔸 Я рекламодатель", "🔹 Я блогер"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("👋 Привет! Кто ты?", reply_markup=markup)
    return CHOOSING

# === Обработка выбора роли ===
async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text
    if "рекламодатель" in role:
        await update.message.reply_text("Напиши, пожалуйста:\n\n1. Название бренда\n2. Ниша\n3. Бюджет\n4. Целевая аудитория")
        return ADVERTISER
    elif "блогер" in role:
        await update.message.reply_text("Заполни анкету:\n\n1. Имя\n2. Ссылка на блог\n3. Тематика\n4. Охват\n5. Цена за рекламу")
        return BLOGGER

# === Сохраняем заявку от рекламодателя ===
async def save_advertiser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    info = (f"\n=== Заявка от рекламодателя ===\n"
            f"Имя: {user.first_name} @{user.username}\n"
            f"{text}\n")
    
    with open("zayavki.txt", "a", encoding="utf-8") as file:
        file.write(info)

    # Уведомление админу
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📩 Новая заявка от рекламодателя:\n{info}")
    # Запись в Google Таблицу
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = ["Рекламодатель", user.first_name, f"@{user.username}", text, timestamp]
    add_to_google_sheet(data)

    await update.message.reply_text("Спасибо! Мы свяжемся с вами скоро. 🙌")
    return ConversationHandler.END

    

# === Сохраняем анкету блогера ===
async def save_blogger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    info = (f"\n=== Анкета блогера ===\n"
            f"Имя: {user.first_name} @{user.username}\n"
            f"{text}\n")
    
    with open("zayavki.txt", "a", encoding="utf-8") as file:
        file.write(info)

    # Уведомление админу
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📩 Новая анкета блогера:\n{info}")

    # Запись в Google Таблицу
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = ["Блогер", user.first_name, f"@{user.username}", text, timestamp]
    add_to_google_sheet(data)
    await update.message.reply_text("Анкета получена! Мы добавим вас в базу ✅")
    return ConversationHandler.END

# === Отмена диалога ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей, отменили 😌")
    return ConversationHandler.END

# === Запуск приложения ===
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_role)],
        ADVERTISER: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_advertiser)],
        BLOGGER: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_blogger)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)

print("✅ Бот запущен. Жди сообщений в Telegram...")
app.run_polling()
