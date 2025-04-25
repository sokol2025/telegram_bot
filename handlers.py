from telegram import Update, ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from sheets import add_advertiser_to_sheet, get_bloggers_data
from datetime import datetime

CHOOSING, ADVERTISER_BRAND, ADVERTISER_NICHE, ADVERTISER_BUDGET, ADVERTISER_AUDIENCE = range(5)
BLOGGER_NAME, BLOGGER_LINKS, BLOGGER_CATEGORIES, BLOGGER_TOPIC, BLOGGER_REACH, BLOGGER_PRICE = range(5, 11)

# Список категорий
CATEGORIES = [
    "Мода", "Красота", "Фитнес и здоровье", "Путешествия",
    "Кулинария", "Технологии", "Геймеры и стримеры",
    "Образование и лайфхаки", "Животные и природа", "Музыка и танцы",
    "Семья и дети", "Искусство и творчество", "Юмор и развлечение",
    "Политика и общественные события"
]

ADMIN_CHAT_ID = 235130655  # Замени на свой

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔸 Я рекламодатель", "🔹 Я блогер"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("👋 Привет! Кто ты?", reply_markup=markup)
    return CHOOSING

# === Выбор роли ===
async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text
    if "рекламодатель" in role:
        keyboard = [["🔍 Показать блогеров", "➡️ Продолжить"]]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Выберите действие:", reply_markup=markup)
        return CHOOSING
    elif "Показать блогеров" in role:
        return await handle_show_bloggers(update, context)
    elif "Продолжить" in role:
        await update.message.reply_text("1️⃣ Название бренда:")
        return ADVERTISER_BRAND
    elif "блогер" in role:
        await update.message.reply_text("1️⃣ Напишите ваше имя:")
        return BLOGGER_NAME

# === Рекламодатель: по шагам ===
async def advertiser_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["brand"] = update.message.text
    await update.message.reply_text("2️⃣ Ниша:")
    return ADVERTISER_NICHE

async def advertiser_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["niche"] = update.message.text
    await update.message.reply_text("3️⃣ Бюджет:")
    return ADVERTISER_BUDGET

async def advertiser_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text("4️⃣ Целевая аудитория:")
    return ADVERTISER_AUDIENCE

async def advertiser_audience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["audience"] = update.message.text
    user = update.message.from_user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = [
        "Рекламодатель",
        user.first_name,
        f"@{user.username}",
        context.user_data["brand"],
        context.user_data["niche"],
        context.user_data["budget"],
        context.user_data["audience"],
        timestamp
    ]
    add_advertiser_to_sheet(data, sheet_name="Рекламодатели")

    info = (
        f"\n=== Заявка от рекламодателя ===\n"
        f"Имя: {user.first_name} @{user.username}\n"
        f"Бренд: {context.user_data['brand']}\n"
        f"Ниша: {context.user_data['niche']}\n"
        f"Бюджет: {context.user_data['budget']}\n"
        f"ЦА: {context.user_data['audience']}\n"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📩 Новая заявка от рекламодателя:\n{info}")
    await update.message.reply_text("Спасибо! Мы свяжемся с вами скоро. 🙌")

    return ConversationHandler.END

# === Блогер: шаги ===
async def save_blogger_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("2️⃣ Укажите ссылки на ваш блог. Отправьте одну ссылку за раз, или напишите 'Готово', чтобы завершить.")
    return BLOGGER_LINKS

async def save_blogger_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    link = update.message.text

    if link.lower() == "готово":
        return await save_blogger_categories(update, context)

    # Добавляем ссылку на блог
    context.user_data.setdefault("links", []).append(link)
    await update.message.reply_text(f"Ссылка добавлена: {link}. Введите следующую ссылку или напишите 'Готово'.")
    return BLOGGER_LINKS

async def save_blogger_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["categories"] = []  # ← ДОБАВЬ ЭТУ СТРОКУ

    keyboard = [[category] for category in CATEGORIES]
    keyboard.append(["Готово"])
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "3️⃣ Выберите категорию вашего блога (можно выбрать несколько):", reply_markup=markup)
    return BLOGGER_TOPIC


async def save_blogger_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text

    if category == "Готово":
        if not context.user_data["categories"]:
            await update.message.reply_text("Вы не выбрали ни одной категории. Пожалуйста, выберите хотя бы одну.")
            return BLOGGER_TOPIC

        await update.message.reply_text("4️⃣ Укажите охват вашего блога:", reply_markup=ReplyKeyboardRemove())
        return BLOGGER_REACH

    if category not in CATEGORIES:
        await update.message.reply_text("Выберите категорию из списка или нажмите 'Готово'.")
        return BLOGGER_TOPIC

    if category not in context.user_data["categories"]:
        context.user_data["categories"].append(category)
        await update.message.reply_text(f"Добавлена категория: {category}. Выберите ещё или нажмите 'Готово'.")
    else:
        await update.message.reply_text(f"Категория {category} уже выбрана. Выберите другую или нажмите 'Готово'.")

    return BLOGGER_TOPIC


async def save_blogger_reach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reach"] = update.message.text
    await update.message.reply_text("5️⃣ Укажите цену за рекламу:")
    return BLOGGER_PRICE

async def save_blogger_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text
    return await finish_blogger(update, context)

# === Завершение анкеты блогера ===
# handlers.py

async def finish_blogger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = context.user_data["name"]
    links = ", ".join(context.user_data.get("links", []))
    categories = ", ".join(context.user_data.get("categories", []))
    reach = context.user_data["reach"]
    price = context.user_data["price"]

    info = (
        f"\n=== Анкета блогера ===\n"
        f"Имя: {user.first_name} @{user.username}\n"
        f"1. {name}\n2. {links}\n3. {categories}\n4. {reach}\n5. {price}\n"
    )

    with open("zayavki.txt", "a", encoding="utf-8") as file:
        file.write(info)

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📩 Новая анкета блогера:\n{info}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = ["Блогер", user.first_name, f"@{user.username}", name, links, categories, reach, price, timestamp]

    # Передаем параметр sheet_name при вызове функции
    add_advertiser_to_sheet(data, sheet_name="Блогеры")

    await update.message.reply_text("✅ Анкета принята! Мы добавим вас в базу.")
    return ConversationHandler.END


# === Просмотр блогеров ===
async def handle_show_bloggers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bloggers = get_bloggers_data()
    if not bloggers:
        await update.message.reply_text("Сейчас в базе нет блогеров.")
        return CHOOSING

    message = "📋 Список блогеров:\n\n"
    for blogger in bloggers:
        message += (
            f"👤 {blogger['Имя анкеты']}\n"
            f"🔗 {blogger['Ссылка']}\n"
            f"📌 {blogger['Тематика']}\n"
            f"👥 Охват: {blogger['Охват']}\n"
            f"💰 Цена: {blogger['Цена']}\n\n"
        )

    await update.message.reply_text(message[:4000])  # Ограничение Telegram на длину сообщения
    return CHOOSING

# === Отмена ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей, отменили 😌")
    return ConversationHandler.END
