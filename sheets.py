import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Устанавливаем разрешения для работы с Google Sheets API
def get_credentials():
    # Обновленный список scopes
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",  # Добавьте это для доступа к файлам на Google Drive
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Telegram bot\telegram-bot-457614-0096237ea079.json", scope)
    client = gspread.authorize(creds)
    return client



# Добавление данных в Google Sheets
def add_to_google_sheet(data, sheet_name):
    client = get_credentials()  # Получаем клиент
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GFaTC879ZZ1I3ZLNWnfxQetJvwmHfkHEzk6ZTPEtPWw/edit?gid=1475063083#gid=1475063083').worksheet(sheet_name)  # Открываем лист по имени
    sheet.append_row(data)  # Добавляем строку

# Получение всех данных блогеров
def get_bloggers_data():
    client = get_credentials()
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GFaTC879ZZ1I3ZLNWnfxQetJvwmHfkHEzk6ZTPEtPWw/edit?gid=1475063083#gid=1475063083').worksheet("Блогеры")
    data = sheet.get_all_records()
    return data

# Получение всех данных рекламодателей
def get_advertisers_data():
    client = get_credentials()
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GFaTC879ZZ1I3ZLNWnfxQetJvwmHfkHEzk6ZTPEtPWw/edit?gid=1475063083#gid=1475063083').worksheet("Рекламодатели")
    data = sheet.get_all_records()
    return data

# Получение данных по категории блогеров
def get_bloggers_by_category(category):
    client = get_credentials()
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GFaTC879ZZ1I3ZLNWnfxQetJvwmHfkHEzk6ZTPEtPWw/edit?gid=1475063083#gid=1475063083').worksheet("Блогеры")
    data = sheet.get_all_records()

    filtered_data = [blogger for blogger in data if category in blogger['Тематика']]
    return filtered_data

# Получение данных блогера по имени
def get_blogger_by_name(name):
    client = get_credentials()
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GFaTC879ZZ1I3ZLNWnfxQetJvwmHfkHEzk6ZTPEtPWw/edit?gid=1475063083#gid=1475063083').worksheet("Блогеры")
    data = sheet.get_all_records()

    blogger_data = [blogger for blogger in data if name.lower() in blogger['Имя'].lower()]
    return blogger_data

# Получение данных блогеров по цене
def get_bloggers_by_price(price_range):
    client = get_credentials()
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GFaTC879ZZ1I3ZLNWnfxQetJvwmHfkHEzk6ZTPEtPWw/edit?gid=1475063083#gid=1475063083').worksheet("Блогеры")
    data = sheet.get_all_records()

    min_price, max_price = map(int, price_range.split('-'))
    filtered_data = [blogger for blogger in data if min_price <= int(blogger['Цена']) <= max_price]
    return filtered_data

# Добавление данных о рекламодателе в Google Sheets
def add_advertiser_to_sheet(data, sheet_name):
    client = get_credentials()  # Получаем клиент
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1GFaTC879ZZ1I3ZLNWnfxQetJvwmHfkHEzk6ZTPEtPWw/edit?gid=1475063083#gid=1475063083').worksheet(sheet_name)  # Открываем лист
    sheet.append_row(data)  # Добавляем строку

# Пример использования: добавление данных о рекламодателе
def add_advertiser_data(brand, niche, budget, audience, user):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [
        "Рекламодатель",
        user.first_name,
        f"@{user.username}",
        brand,
        niche,
        budget,
        audience,
        timestamp
    ]
    add_advertiser_to_sheet(data, sheet_name="Рекламодатели")  # Теперь передаем sheet_name
