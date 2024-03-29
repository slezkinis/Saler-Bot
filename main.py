import telebot
from dotenv import load_dotenv
import os
from telebot import types
from db import SQL

# Bot_setiings
db = SQL()
load_dotenv()
bot = telebot.TeleBot(os.environ['TG_TOKEN'])
creator_chat_id = os.environ['CREATOR_CHAT_ID']
payment_token = os.environ['PAYMENT_TOKEN']
with open('link.txt', 'r') as file:
    disk_link = file.read()
admin = False
is_creating_sections = False
selected_adm_section = ''
next_added = ''
info_created_product = []
info_created_promo = []
promocodes_users = []
text_to_send = ''


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and m.text == '⚙️ Настройка магазина')
def settings(message):
    global admin
    admin = True
    markup = types.InlineKeyboardMarkup()
    promo = types.InlineKeyboardButton('Промокоды', callback_data='promo')
    cat = types.InlineKeyboardButton('Товары', callback_data='sections')
    link = types.InlineKeyboardButton('Ссылка', callback_data='yandex_link')
    send_to_all = types.InlineKeyboardButton('Рассылка', callback_data='send_to_all')
    markup.add(promo)
    markup.row()
    markup.add(cat)
    markup.row()
    markup.add(link)
    markup.row()
    markup.add(send_to_all)
    markup.row()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.chat.id, 'Это настройка магазина!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'send_to_all')
def send_to_all(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    global next_added
    next_added = 'send_to_all'
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Отменить', callback_data='cancel_product')
    markup.add(close)
    bot.send_message(message.message.chat.id, 'Введите сообщение, которое будет отправлено всем пользователям:', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'send_to_all' in next_added)
def need_send(message):
    global next_added, text_to_send
    text_to_send = message.text
    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton('✅', callback_data=f'yes_send_to_all')
    no = types.InlineKeyboardButton('❌', callback_data=f'no_send_to_all')
    markup.add(yes, no)
    next_added = ''
    bot.send_message(message.chat.id, f'Вы уверены, что хотите отправить Ваше сообщение всем пользователям?', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'yes_send_to_all')
def yes_send_to_all(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    global text_to_send
    users = db.get_all_users()
    for user in users:
        bot.send_message(int(user[0]), text_to_send)
    text_to_send = ''
    bot.send_message(message.message.chat.id, f'Сообщение отправлено {len(users)} пользователям!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'no_send_to_all')
def no_send_to_all(message):
    global text_to_send
    text_to_send = ''
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.message.chat.id, f'Отменено!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'yandex_link')
def yandex_link(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    change_link = types.InlineKeyboardButton('Изменить ссылку', callback_data='change_link')
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(change_link, close)
    bot.send_message(message.message.chat.id, f'Такая ссылка установлена сейчас: {disk_link}', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'change_link')
def change_link(message):
    global next_added
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Отменить', callback_data='cancel_product')
    markup.add(close)
    next_added = 'yandex_link'
    bot.send_message(message.message.chat.id, 'Введите ссылку:', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'yandex_link' in next_added)
def promo_price(message):
    global next_added, disk_link
    next_added = ''
    with open('link.txt', 'w') as file:
        file.write(message.text)
    disk_link = message.text
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.chat.id, f'Новая ссылка: {disk_link}', reply_markup=markup)
    

@bot.callback_query_handler(func=lambda c: c.data == 'promo')
def promo_settings(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    promocodes = db.get_all_promocodes()
    new = types.InlineKeyboardButton('✏️ Добавить новый промокод', callback_data='new_promo')
    markup.add(new)
    for i in promocodes:
        markup.add(types.InlineKeyboardButton(f'{i[1]}, {i[2]}', callback_data=f'del_promo_{i[0]}'))
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.message.chat.id, 'Вот все промокоды. Нажмите на промокод, чтобы удалить:', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'del_promo_' in c.data)
def delete_promo(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    id_promo = int(message.data.replace('del_promo_', ''))
    promo_title = db.delete_promo(id_promo)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.message.chat.id, f'Промокод {promo_title} удалён!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'new_promo')
def create_promo(message):
    global info_created_promo, next_added
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🚫 Отменить', callback_data='cancel_product'))
    info_created_promo = []
    next_added = 'title'
    bot.send_message(message.message.chat.id, 'Введите промокод:', reply_markup=markup)
    

@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'title' in next_added)
def promo_price(message):
    global info_created_promo, next_added
    info_created_promo.append(message.text)
    next_added = 'price'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🚫 Отменить', callback_data='cancel_product'))
    bot.send_message(message.chat.id, 'Введите цену', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'price' in next_added)
def yes_create_promo(message):
    global info_created_promo, next_added
    info_created_promo.append(int(message.text))
    next_added = ''
    db.create_promocode(info_created_promo[0], info_created_promo[1])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='cancel_product'))
    bot.send_message(message.chat.id, f'Создан промокод {info_created_promo[0]}', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == 'sections')
def all_category_settings(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    global admin
    admin = True
    markup = types.InlineKeyboardMarkup()
    sections = db.get_all_sections()
    new = types.InlineKeyboardButton('✏️ Добавить новую категорию', callback_data='new_section')
    markup.add(new)
    for section in sections:
        b1 = types.InlineKeyboardButton(section[0], callback_data=f'set-adm_{section[1]}')
        markup.add(b1)
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.message.chat.id, 'Вот все категории:', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'set-adm_' in c.data)
def section_settings(message):
    global selected_adm_section
    bot.delete_message(message.message.chat.id, message.message.message_id)
    all_results = db.get_products_by_section(int(message.data.replace("set-adm_", "")))
    markup = types.InlineKeyboardMarkup()
    delete = types.InlineKeyboardButton('🗑️ Удалить эту категорию', callback_data=f'delete_category_{message.data.replace("set-adm_", "")}')
    add = types.InlineKeyboardButton('➕ Добавить товар в эту категорию', callback_data=f'add_product_in_{message.data.replace("set-adm_", "")}')
    markup.add(delete, add)
    for product in all_results:
        button1 = types.InlineKeyboardButton(product[1], callback_data=f'product_set_{product[0]}')
        markup.add(button1)
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    selected_adm_section = db.get_section(message.data.replace('set-adm_', ''))
    bot.send_message(message.message.chat.id, f'Это раздел для редактирования категории "{selected_adm_section[0]}"', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: c.data == 'new_section')
def add_section(message):
    global is_creating_sections
    bot.delete_message(message.message.chat.id, message.message.message_id)
    is_creating_sections = True
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_section')
    markup.add(cancel)
    bot.send_message(message.message.chat.id, 'Напишите название для новой категории', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'product_set_' in c.data)
def delete_product(message):
    markup = types.InlineKeyboardMarkup()
    product = db.get_product(message.data.replace("product_set_", ""))
    bot.delete_message(message.message.chat.id, message.message.message_id)
    yes = types.InlineKeyboardButton('✅', callback_data=f'yes_product_{message.data.replace("product_set_", "")}')
    no = types.InlineKeyboardButton('❌', callback_data=f'no_product_{message.data.replace("product_set_", "")}')
    markup.add(yes, no)
    bot.send_message(message.message.chat.id, f'Вы уверены, что хотите удалить товар "{product[1]}', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'yes_product_' in c.data)
def delete(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    global admin
    admin = False
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    product = db.get_product(message.data.replace("yes_product_", ""))
    os.remove(product[7])
    db.delete_product(message.data.replace("yes_product_", ""))
    users = db.get_all_users()
    for user in users:
        buy = user[2].split('; ')
        if f'{message.data.replace("yes_product_", "")}' in buy:
            buy.remove(f'{message.data.replace("yes_product_", "")}')
        db.update_user_buy('; '.join(buy), user[0])
    bot.send_message(message.message.chat.id, f'Товар "{product[1]}" удалён!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'no_product_' in c.data)
def cancel_delete(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    global admin
    admin = False
    product = db.get_product(message.data.replace("no_product_", ""))
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    bot.send_message(message.message.chat.id, f'Товар "{product[1]}" не удалён!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'delete_category_' in c.data)
def delete_category(message):
    markup = types.InlineKeyboardMarkup()
    bot.delete_message(message.message.chat.id, message.message.message_id)
    category = db.get_section(message.data.replace("delete_category_", ""))
    yes = types.InlineKeyboardButton('✅', callback_data=f'yes_category_{message.data.replace("delete_category_", "")}')
    no = types.InlineKeyboardButton('❌', callback_data=f'no_category_{message.data.replace("delete_category_", "")}')
    markup.add(yes, no)
    bot.send_message(message.message.chat.id, f'Вы уверены, что хотите удалить категорию "{category[0]} вместе со всеми принадлежащими ей товарами?', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'cancel_product' in c.data)
def cancel_product(message):
    global next_added, info_created_product, promo
    next_added = ''
    info_created_product = []
    promo = []
    bot.delete_message(message.message.chat.id, message.message.message_id)
    global admin
    admin = True
    markup = types.InlineKeyboardMarkup()
    promo = types.InlineKeyboardButton('Промокоды', callback_data='promo')
    cat = types.InlineKeyboardButton('Товары', callback_data='sections')
    link = types.InlineKeyboardButton('Ссылка', callback_data='yandex_link')
    send_to_all = types.InlineKeyboardButton('Рассылка', callback_data='send_to_all')
    markup.add(promo)
    markup.row()
    markup.add(cat)
    markup.row()
    markup.add(link)
    markup.row()
    markup.add(send_to_all)
    markup.row()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.message.chat.id, 'Это настройка магазина!', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'add_product_in_' in c.data)
def add_new_product(message):
    global next_added
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    bot.delete_message(message.message.chat.id, message.message.message_id)
    next_added = f'Название_{message.data.replace("add_product_in_", "")}'
    bot.send_message(message.message.chat.id, 'Напишите название товара', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and "Название_" in next_added)
def name(message):
    global next_added, info_created_product
    # bot.delete_message(message.chat.id, message.message_id)
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    next_added = f'Описание_{next_added.replace("Название_", "")}'
    info_created_product.append(message.text)
    bot.send_message(message.chat.id, 'Напишите описание товара', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'Описание_' in next_added)
def description(message):
    global next_added, info_created_product
    next_added = f'Ссылка_{next_added.replace("Описание_", "")}'
    # bot.delete_message(message.chat.id, message.message_id)
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    info_created_product.append(message.text)
    bot.send_message(message.chat.id, 'Напишите ссылку на курс', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'Ссылка_' in next_added)
def link(message):
    global next_added, info_created_product
    next_added = f'C_Цена_{next_added.replace("Ссылка_", "")}'
    # bot.delete_message(message.chat.id, message.message_id)
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    info_created_product.append(message.text)
    bot.send_message(message.chat.id, 'Напишите старую цену на курс (в рублях)', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'C_Цена_' in next_added)
def old_price(message):
    global next_added, info_created_product
    next_added = f'Н_Цена_{next_added.replace("C_Цена_", "")}'
    # bot.delete_message(message.chat.id, message.message_id)
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    info_created_product.append(message.text)
    bot.send_message(message.chat.id, 'Напишите новую цену на курс (в рублях)', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'Н_Цена_' in next_added)
def new_price(message):
    global next_added, info_created_product
    # bot.delete_message(message.chat.id, message.message_id)
    next_added = f'Image_{next_added.replace("Н_Цена_", "")}'
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton('🚫 Отмена', callback_data='cancel_product')
    markup.add(cancel)
    info_created_product.append(int(message.text))
    info_created_product.append(next_added.replace('Image_', ''))
    bot.send_message(message.chat.id, 'Отправьте картинку для курса', reply_markup=markup)


@bot.message_handler(content_types=['photo'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and 'Image_' in next_added)
def image(message):
    global next_added, info_created_product
    markup = types.InlineKeyboardMarkup()
    # bot.delete_message(message.chat.id, message.message_id)
    yes = types.InlineKeyboardButton('✅', callback_data=f'add')
    no = types.InlineKeyboardButton('❌', callback_data=f'not_add')
    markup.add(yes, no)
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = f'./images/{info_created_product[0]}.jpg'
    info_created_product.append(src)
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    next_added = 'Ок'
    bot.send_message(message.chat.id, f'Название: {info_created_product[0]}\nОписание: {info_created_product[1]}\nСсылка: {info_created_product[2]}\nСтарая цена: {info_created_product[3]} руб.\nНовая цена: {info_created_product[4]} руб.', reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'Ок' in next_added)
def ok(message):
    global next_added, info_created_product, admin
    next_added = ''
    bot.delete_message(message.message.chat.id, message.message.message_id)
    admin = False
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    if message.data == 'add':
        db.create_product(info_created_product)
        bot.send_message(message.message.chat.id, 'Товар добавлен!', reply_markup=markup)
        info_created_product = []
    else:
        bot.send_message(message.message.chat.id, 'Товар не добавлен!', reply_markup=markup)
        info_created_product = []
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'yes_category_' in c.data)
def delete_category(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    name = db.get_section(str(message.data).replace('yes_category_', ''))
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    db.delete_section(name[1])
    all_results = db.get_products_by_section(name[1])
    count = 0
    for product in all_results:
        users = db.get_all_users()
        for user in users:
            buy = user[2].split('; ')
            if product[0] in buy:
                buy.remove(product[0])
            db.update_user_buy('; '.join(buy), user[0])
        db.delete_product(product[0])
        count += 1
    bot.send_message(message.message.chat.id, f'Удалена категория "{name[0]} и {count} шт товаров!', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'no_category_' in c.data)
def delete_category(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    markup = types.InlineKeyboardMarkup()
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    bot.send_message(message.message.chat.id, f'Удаление категории отменено', reply_markup=markup)
    bot.answer_callback_query(message.id)


@bot.message_handler(content_types=['text'], func=lambda m: str(m.chat.id) == str(creator_chat_id) and is_creating_sections)
def correct_section(message):
    db.create_section(message.text)
    markup = types.InlineKeyboardMarkup()
    global is_creating_sections
    is_creating_sections = False
    go_home = types.InlineKeyboardButton('⚙️ Вернуться к редактированию', callback_data='cancel_section')
    markup.add(go_home)
    bot.send_message(message.chat.id, f'Создана новая категория с именем {message.text}!', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    all_results = db.get_all_users()
    all_users = [i[0] for i in all_results]
    if message.chat.id not in all_users:
        if len(message.text.split(' ')) == 2:
            markup = types.InlineKeyboardMarkup()
            close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
            markup.add(close)
            ref_chat_id = message.text.split(' ')[1]
            db.add_user((message.chat.id, message.chat.username, '', 0, ref_chat_id))
        else:
            db.add_user((message.chat.id, message.chat.username, '', 0, -1))
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    shop = types.KeyboardButton('🛒 Товары')
    not_pay = types.KeyboardButton('❗️Получить доступ ко всему❗️')
    help = types.KeyboardButton('📖 Помощь')
    info = types.KeyboardButton('ℹ️ Информация')
    profile = types.KeyboardButton('📱 Профиль')
    ref = types.KeyboardButton('💸 Реферальная система')
    markup.add(shop, not_pay, profile, ref, info, help)
    if str(message.chat.id) == str(creator_chat_id):
        admin1 = types.KeyboardButton('⚙️ Настройка магазина')
        markup.add(admin1)
    bot.send_message(message.chat.id, 'Привет! Добро пожаловать в онлайн магазин', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.text == 'ℹ️ Информация')
def info(message):
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    text = '''
Привет дорогой друг.🎉
расскажем немного о Нас.

🧰Наша команда покупает дорогостоящие программы, курсы и обучение в разных направлениях через "Совместные покупки"🛍

🎈Мы даём доступ всем заинтересованным за минимальное вознаграждение получить желаемый контент который поможет изменить в лучшую сторону вашу жизнь.

🎁Мы гарантируем что Ваша экономия составит более 90%
от реальной стоимости выбранного Вами контента.🎊
'''
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '💸 Реферальная система')
def referal_system(message):
    ch = db.get_user(message.chat.id)[3]
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    link = f't.me/{bot.user.username}?start={message.chat.id}'
    bot.send_message(message.chat.id, f'В нашем онлайн магазине действует акция! Если ты приглашаешь одного пользователя и он покупает любой наш курс, то ты получаешь любой курс на твой выбор совершенно бесплатно! А если ты пригласишь 5-х пользователей и они купят у нас один курс, то ты получишь доступ ко всем курсам навсегда!\nВот твоя реферальная ссылка: {link}\nВот сколько людей перешли по твоей ссылке и купили у нас что-то: {ch}', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '📖 Помощь')
def help(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Перейти', url='https://t.me/Mr_Biskvit'))
    markup.row()
    markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
    bot.send_message(message.chat.id, '✍️ По всем возникающим вопросам пишите @Mr_Biskvit', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '❗️Получить доступ ко всему❗️')
def get_all(message):
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton('💳 Купить за 1499 руб', callback_data='sale')
    promocode = types.InlineKeyboardButton('Ввести промокод', callback_data='enter_promo')
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(ok)
    markup.row()
    markup.add(promocode)
    markup.add(close)
    text = '''
🔥🔥🔥Максимальная выгода🔥🔥🔥

За 1490 рублей Вам откроется весь каталог в полном объеме.
Если учесть что цена за 1 товар составляет от 500 до 900 рублей.

✅Ваша выгода неизмерима велика
поскольку практически ежедневно добавляется новый товар к которому у вас также будет полный доступ.🔐💯
'''
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda m: m.data == 'enter_promo')
def enter_promo(message):
    global promocodes_users
    bot.delete_message(message.message.chat.id, message.message.message_id)
    promocodes_users.append(message.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Отменить', callback_data='cancel_enter')
    markup.add(close)
    bot.send_message(message.message.chat.id, 'Введите промокод:', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.chat.id in promocodes_users)
def check_promo(message):
    global promocodes_users
    promocode = db.get_promocode(message.text)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Отменить', callback_data='cancel_enter')
    markup.add(close)
    if promocode is None:
        bot.send_message(message.chat.id, 'Неверный промокод! Попробуйте ещё раз', reply_markup=markup)
        return
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.chat.id, f'Поздравляю! Для тебя скидка! Все товары за {promocode[2]} руб, вместо 1499 руб.', reply_markup=markup)
    try:
        promocodes_users.remove(message.chat.id)
    except:
        _ = 1
    user = db.get_user(message.chat.id)
    users_buy = user[2]
    if int(promocode[2]) == 0:
        buy_products = user[2]
        if not buy_products and user[4] != -1:
            ref = db.get_user(user[4])
            if ref[3] == 0:
                bot.send_message(ref[0], f'Поздравляю! Пользователь, перешедший по твоей ссылке только что купил у нас курс! 🎆 Теперь ты можешь получить любой наш курс совершенно бесплатно! Пригласи ещё 4-х людей и ты получишь полный доступ ко всем курсам НАВСЕГДА!')
            if ref[3] == 4:
                bot.send_message(ref[0], f'Поздравляю! Ровно 5 пользователей перешли по твоей реферальной ссылке и купили у нас курс 🎆 Ты получаешь доступ ко всем курсам НАВСЕГДА!')
                db.update_user_buy('all', ref[0])
                db.update_user_money(user[4], -1)
                bot.send_message(message.chat.id, f'Ссылка: {disk_link}', reply_markup=markup)
            db.update_user_money(user[4], ref[3] + 1)
        db.update_user_buy('all', message.chat.id)
        bot.send_message(message.chat.id, f'Ссылка: {disk_link}', reply_markup=markup)
    else:
        if users_buy != 'all':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(f"Заплатить", pay=True))
            keyboard.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            prices = [types.LabeledPrice(label=f'Доступ ко всем товарам', amount=int(promocode[2]) * 100)]
            bot.send_invoice(
                message.chat.id,
                'Доступ',
                f'Доступ ко всем товарам', is_flexible=False, prices=prices, provider_token=payment_token, currency="rub", invoice_payload='sale', reply_markup=keyboard, )
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.send_message(message.chat.id, f'Вы уже купили все товары в этом боте!\nСсылка: {disk_link}', reply_markup=markup)


@bot.callback_query_handler(func=lambda m: m.data == 'cancel_enter')
def cancel_enter_зкщьщ(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    try:
        promocodes_users.remove(message.message.chat.id)
    except:
        1 == 1
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton('💳 Купить за 1499 руб', callback_data='sale')
    promocode = types.InlineKeyboardButton('Ввести промокод', callback_data='enter_promo')
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(ok)
    markup.row()
    markup.add(promocode)
    markup.add(close)
    bot.send_message(message.message.chat.id, 'Внимание❗️ Вы можете получить все товары за 1499 руб❗️ Скорее покупайте и наслаждайтесь', reply_markup=markup)


@bot.callback_query_handler(func=lambda m: m.data == 'sale')
def get_all_send_invoice(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    prices = []
    user = db.get_user(message.message.chat.id)
    users_buy = user[2]
    if users_buy != 'all':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(f"Заплатить", pay=True))
        keyboard.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
        prices = [types.LabeledPrice(label=f'Доступ ко всем товарам', amount=149900)]
        bot.send_invoice(
            message.message.chat.id,
            'Доступ',
            f'Доступ ко всем товарам', is_flexible=False, prices=prices, provider_token=payment_token, currency="rub", invoice_payload='sale', reply_markup=keyboard, )
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
        bot.send_message(message.message.chat.id, f'Вы уже купили все товары в этом боте!\nСсылка: {disk_link}', reply_markup=markup)
    bot.answer_callback_query(message.id)
    


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '🛒 Товары')
def shop(message):
    all_results = db.get_all_users()
    all_users = [i[0] for i in all_results]
    if message.chat.id not in all_users:
        db.add_user((message.chat.id, message.chat.username, '', 0, -1))
    all_results = db.get_all_sections()
    markup = types.InlineKeyboardMarkup()
    for product in all_results:
        button1 = types.InlineKeyboardButton(product[0], callback_data=f'category_{product[1]}')
        markup.add(button1)
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    bot.send_message(message.chat.id, 'Вот список категорий', reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda m: m.text == '📱 Профиль')
def profile(message):
    all_results = db.get_all_users()
    all_users = [i[0] for i in all_results]
    if message.chat.id not in all_users:
       db.add_user((message.chat.id, message.chat.username, '', 0, -1))
    user = db.get_user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    name = message.chat.first_name
    count = 0
    count_products = 0
    if user[2] != 'all':
        users_buy = user[2].split('; ')
        if '' in users_buy:
            users_buy.remove('')
        for product_name in users_buy:
            product = db.get_product(product_name)
            count += product[5]
            count_products += 1
        if not name:
            name = 'Не указано'
        text = f'🙍‍♂ Пользователь: {message.chat.first_name}\n🆔 ID: {message.chat.id}\n------------------\n🛒 Количество покупок: {count_products} шт.\n💰 Общая сумма: {count} руб.'
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        if not name:
            name = 'Не указано'
        text = f'🙍‍♂ Пользователь: {message.chat.first_name}\n🆔 ID: {message.chat.id}\n------------------\n🛒 Количество покупок: КУПИЛ ВСЁ!\n💰 Общая сумма: ∞ руб.'
        bot.send_message(message.chat.id, text, reply_markup=markup)
    

@bot.message_handler(commands=['add'], func=lambda c: str(c.chat.id) == str(creator_chat_id))
def add(message):
    user = db.get_user(message.chat.id)
    db.update_user_money(message.chat.id, user[3] + 1)
#     text = message.text.split()
#     if not text[1]:
#         bot.send_message(message.chat.id, 'Проверьте, указали ли Вы ID человека!')
#         return
#     user = db.get_user(int(text[1]))
#     if not user:
#         bot.send_message(message.chat.id, 'Пользователь с таким ID в базе данных не найден!')
#     markup = types.InlineKeyboardMarkup()
#     yes = types.InlineKeyboardButton('✅', callback_data=f'ok_{text[1]}')
#     no = types.InlineKeyboardButton('❌', callback_data=f'not_{text[1]}')
#     markup.add(yes, no)
#     bot.send_message(message.chat.id, f'Вы уверены, что хотите выдать пользователю с ID {text[1]} все товары?', reply_markup=markup)


# @bot.callback_query_handler(func=lambda c: 'ok_' in c.data)
# def add_t(message):
#     bot.delete_message(message.message.chat.id, message.message.message_id)
#     markup = types.InlineKeyboardMarkup()
#     close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
#     markup.add(close)
#     all_results = db.get_all_products()
#     products = [i[0] for i in all_results]
#     db.update_user_buy('; '.join(products), message.data.replace('ok_', ''))
#     bot.send_message(message.message.chat.id, f'Пользователю с ID {message.data.replace("ok_", "")} выдано {len(products)} шт товаров!', reply_markup=markup)
#     bot.answer_callback_query(message.id)
#     bot.send_message(message.data.replace('ok_', ''), '❗️Вам выдали доступ ко всем курсам! Поздравляем!❗️', reply_markup=markup)
    

# @bot.callback_query_handler(func=lambda c: 'not_' in c.data)
# def add_t(message):
#     bot.delete_message(message.message.chat.id, message.message.message_id)
#     markup = types.InlineKeyboardMarkup()
#     close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
#     markup.add(close)
#     bot.send_message(message.message.chat.id, f'Операция отменена!', reply_markup=markup)
#     bot.answer_callback_query(message.id)


def check_sections(message):
    all_results = db.get_all_sections()
    data = [str(product[1]) for product in all_results]
    if message.data.replace('category_', '') in data and 'category_' in message.data:
        return True
    else:
        return False


def check_products(message):
    all_results = db.get_all_products()
    data = [str(product[0]) for product in all_results]
    if message.data.replace('product_', '') in data and 'product_' in message.data:
        return True
    else:
        return False


@bot.callback_query_handler(func=check_sections)
def inlin_sections(message):
    section = db.get_section(int(message.data.replace('category_', '')))
    all_results = db.get_products_by_section(section[1])
    markup = types.InlineKeyboardMarkup(row_width=1)
    count = 0
    buttons = []
    # buy_all = types.InlineKeyboardButton('💳 Купить всю категорию', callback_data=f'cat_{message.data.replace("category_", "")}')
    # markup.add(buy_all)
    for product in all_results:
        button1 = types.InlineKeyboardButton(product[1], callback_data=f'product_{product[0]}')
        buttons.append(button1)
        if count == 2:
            for j in buttons:
                markup.add(j)
            count = 0
            buttons = []
        else:
            count += 1
    for j in buttons:
        markup.add(j)
    button1 = types.InlineKeyboardButton("Назад 🔙", callback_data="home")
    markup.add(button1)
    bot.delete_message(message.message.chat.id, message.message.message_id)
    bot.send_message(message.message.chat.id, f'Товары из категории "{section[0]}" ⬇️', reply_markup=markup)
    bot.answer_callback_query(message.id)


# @bot.callback_query_handler(func=lambda c: 'cat_' in c.data)
# def buy_category(message):
#     bot.delete_message(message.message.chat.id, message.message.message_id)
#     prices = []
#     user = db.get_user(message.message.chat.id)
#     users_buy = user[2].split('; ')
#     if '' in users_buy:
#         users_buy.remove('')
#     section = db.get_section(message.data.replace('cat_', ''))
#     all_results = db.get_products_by_section(message.data.replace('cat_', ''))
#     data = [str(i[0]) for i in all_results]
#     links = []
#     for product in all_results:
#         if str(product[0]) not in users_buy:
#             price = types.LabeledPrice(label=f'Доступ к курсу "{product[1]}"', amount=int(product[5]) * 100)
#             prices.append(price)
#         links.append(f'Название: {product[0]}\nОписание: {product[1]}\nЦена: {product[3]} руб.\nСсылка на курс "{product[0]}": {product[2]}\n\n')
#     links = "\n".join(links)
#     markup = types.InlineKeyboardMarkup()
#     button1 = types.InlineKeyboardButton("Назад к категории 🔙", callback_data=f'category_{product[5]}')
#     markup.add(button1)
#     if prices:
#         keyboard = types.InlineKeyboardMarkup()
#         keyboard.add(types.InlineKeyboardButton(f"Заплатить", pay=True))
#         keyboard.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
#         bot.send_invoice(
#             message.message.chat.id,
#             'Доступ',
#             f'Доступ к категории "{section[0]}', is_flexible=False, prices=prices, provider_token=payment_token, currency="rub", invoice_payload='; '.join(data), reply_markup=keyboard, )
#     else:
#         bot.send_message(message.message.chat.id, f'Вы уже купили все товары из этой категории\n{links}', reply_markup=markup)

@bot.callback_query_handler(func=check_products)
def inlin_product(message):
    markup2 = types.InlineKeyboardMarkup()
    markup = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
    markup.add(close)
    product = db.get_product(message.data.replace('product_', ''))
    with open(product[7], 'rb') as file:
        image = file.read()
    buy_products = db.get_user(message.message.chat.id)[2]
    if str(product[0]) not in buy_products.split('; ') and buy_products != 'all':
        buy = types.InlineKeyboardButton("Купить 💳", callback_data=f"{product[0]}_buy")
        ch = db.get_user(message.message.chat.id)[3]
        if ch:     
            get_free = types.InlineKeyboardButton('Получить бесплатно', callback_data=f'free_{product[0]}')
        button1 = types.InlineKeyboardButton("Назад к категории 🔙", callback_data=f'category_{product[6]}')
        if ch:
            markup2.add(buy, get_free, button1)
        else:
            markup2.add(buy, button1)
    else:
        buy = types.InlineKeyboardButton("Отправить ссылку", callback_data=f"{product[0]}_buy")
        button1 = types.InlineKeyboardButton("Назад к категории 🔙", callback_data=f'category_{product[6]}')
        markup2.add(buy, button1)
    bot.delete_message(message.message.chat.id, message.message.message_id)
    bot.send_photo(message.message.chat.id, image, reply_markup=markup)
    bot.send_message(message.message.chat.id, f"Название: {product[1]}\nОписание: {product[2]}\nЦена: <s>{product[4]} руб</s>    <b>{product[5]} руб</b>", parse_mode='html', reply_markup=markup2)
    bot.answer_callback_query(message.id)


@bot.callback_query_handler(func=lambda c: 'free_' in c.data)
def get_product_free(message):
    markup = types.InlineKeyboardMarkup()
    bot.delete_message(message.message.chat.id, message.message.message_id)
    # product = db.get_product(message.data.replace('free_', ''))
    # people_price = product[5] // 50
    ch = db.get_user(message.message.chat.id)[3]
    if ch >= 1:
        markup.add(types.InlineKeyboardButton('Потратить', callback_data=f'get_{message.data.replace("free_", "")}'))
        markup.add(types.InlineKeyboardButton('🔙 К товару', callback_data=f'product_{message.data.replace("free_", "")}'))
        bot.send_message(message.message.chat.id, 'Ты можешь получить этот курс бесплатно! Берёшь?', reply_markup=markup)
        return

@bot.callback_query_handler(func=lambda c: 'get_' in c.data)
def buy_product_free(message):
    bot.delete_message(message.message.chat.id, message.message.message_id)
    product = db.get_product(message.data.replace('get_', ''))
    markup = types.InlineKeyboardMarkup()
    section = types.InlineKeyboardButton('Обратно к категории 🔙', callback_data=f'category_{str(product[6])}')
    home = types.InlineKeyboardButton("На главный экран 🏠", callback_data="close")
    links = []
    markup.add(section, home)
    user = db.get_user(message.message.chat.id)
    buy_products = user[2].split('; ')
    if '' in buy_products:
        buy_products.remove('')
    if not buy_products and user[4] != -1:
        ref = db.get_user(user[4])
        db.update_user_money(user[4], ref[3] + 1)
    buy_products.append(str(product[0]))
    db.update_user_buy('; '.join(buy_products), message.message.chat.id)
    db.update_user_money(message.message.chat.id, user[3] - 1)
    links.append(f'Название: {product[1]}\nОписание: {product[2]}\nЦена: {product[5]} руб.\nСсылка на курс "{product[1]}": {product[3]}\n\n')
    links = "\n".join(links)
    bot.send_message(message.message.chat.id, f'Спасибо за покупку! \n{links}', reply_markup=markup)

@bot.callback_query_handler(func=lambda c:True)
def inlin(message):
    # data = message.message.json['reply_markup']['inline_keyboard'][0][0]['callback_data']
    if message.data == 'close':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.answer_callback_query(message.id)
    if message.data == 'home':
        bot.delete_message(message.message.chat.id, message.message.message_id)
        all_results = db.get_all_sections()
        markup = types.InlineKeyboardMarkup()
        for product in all_results:
            button1 = types.InlineKeyboardButton(product[0], callback_data=f'category_{product[1]}')
            markup.add(button1)
        close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
        markup.add(close)
        bot.send_message(message.message.chat.id, 'Вот список категорий', reply_markup=markup)
        bot.answer_callback_query(message.id)
    if message.data == 'cancel_section':
        global is_creating_sections
        is_creating_sections = False
        bot.delete_message(message.message.chat.id, message.message.message_id)
        global admin
        admin = True
        markup = types.InlineKeyboardMarkup()
        sections = db.get_all_sections()
        new = types.InlineKeyboardButton('✏️ Добавить новую категорию', callback_data='new_section')
        markup.add(new)
        for section in sections:
            b1 = types.InlineKeyboardButton(section[0], callback_data=f'set-adm_{section[1]}')
            markup.add(b1)
        close = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
        markup.add(close)
        bot.send_message(message.message.chat.id, 'Это настройка магазина! Вот все категории', reply_markup=markup)
    if '_buy' in message.data:
        data = message.message.json['reply_markup']['inline_keyboard'][0][0]['callback_data'].replace('_buy', '')
        product = db.get_product(message.data.replace('_buy', ''))
        buy_products = db.get_user(message.message.chat.id)[2].split('; ')
        if data not in buy_products and db.get_user(message.message.chat.id)[2] != 'all':
            price = types.LabeledPrice(label=f'Доступ к курсу "{product[1]}"', amount=int(product[5]) * 100)
            bot.delete_message(message.message.chat.id, message.message.message_id)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(f"💲Заплатить", pay=True))
            keyboard.add(types.InlineKeyboardButton('🚫 Закрыть', callback_data='close'))
            bot.send_invoice(
                message.message.chat.id,
                product[1],
                f'Доступ к курсу "{product[1]}"', is_flexible=False, prices=[price], provider_token=payment_token, currency="rub", invoice_payload=product[0], reply_markup=keyboard)
        else:
            markup = types.InlineKeyboardMarkup()
            section = types.InlineKeyboardButton('Обратно к категории 🔙', callback_data=f'category_{product[6]}')
            home = types.InlineKeyboardButton('🚫 Закрыть', callback_data='close')
            markup.add(section, home)
            bot.delete_message(message.message.chat.id, message.message.message_id)
            bot.send_message(message.message.chat.id, f'Вы уже купили этот курс! Вот ссылка: {product[3]}', reply_markup=markup)
        bot.answer_callback_query(message.id)


@bot.pre_checkout_query_handler(lambda h: True)
def good(message):
    bot.answer_pre_checkout_query(message.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def good(message):
    if message.successful_payment.invoice_payload != 'sale':
        bot.delete_message(message.chat.id, message.message_id)
        product = db.get_product(message.successful_payment.invoice_payload)
        markup = types.InlineKeyboardMarkup()
        section = types.InlineKeyboardButton('Обратно к категории 🔙', callback_data=f'category_{str(product[6])}')
        home = types.InlineKeyboardButton("На главный экран 🏠", callback_data="close")
        links = []
        markup.add(section, home)
        user = db.get_user(message.chat.id)
        buy_products = user[2].split('; ')
        if '' in buy_products:
            buy_products.remove('')
        if not buy_products and user[4] != -1:
            ref = db.get_user(user[4])
            if ref[3] == 0:
                bot.send_message(ref[0], f'Поздравляю! Пользователь, перешедший по твоей ссылке только что купил у нас курс! 🎆 Теперь ты можешь получить любой наш курс совершенно бесплатно!')
            if ref[3] == 4:
                bot.send_message(ref[0], f'Поздравляю! Ровно 5 пользователей перешли по твоей реферальной ссылке и купили у нас курс 🎆 Ты получаешь доступ ко всем курсам НАВСЕГДА!')
                user_ref = db.get_user(ref[0])
                buy_products_ref = user_ref[2].split('; ')
                for product in db.get_all_products():
                    if str(product[0]) not in buy_products_ref:
                        buy_products_ref.append(str(product[0]))
                    if '' in buy_products_ref:
                        buy_products_ref.remove('')
                db.update_user_buy('; '.join(buy_products_ref), ref[0])
                db.update_user_money(user[4], -1)
                bot.send_message(message.chat.id, f'Ссылка: {disk_link}', reply_markup=markup)
            db.update_user_money(user[4], ref[3] + 1)
        buy_products.append(str(product[0]))
        db.update_user_buy('; '.join(buy_products), message.chat.id)
        links.append(f'Название: {product[1]}\nОписание: {product[2]}\nЦена: {product[5]} руб.\nСсылка на курс "{product[1]}": {product[3]}\n\n')
        links = "\n".join(links)
        bot.send_message(message.chat.id, f'Спасибо за покупку!\n{links}', reply_markup=markup)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        markup = types.InlineKeyboardMarkup()
        home = types.InlineKeyboardButton("🚫 Закрыть", callback_data="close")
        links = []
        user = db.get_user(message.chat.id)
        buy_products = user[2]
        if not buy_products and user[4] != -1:
            ref = db.get_user(user[4])
            if ref[3] == 0:
                bot.send_message(ref[0], f'Поздравляю! Пользователь, перешедший по твоей ссылке только что купил у нас курс! 🎆 Теперь ты можешь получить любой наш курс совершенно бесплатно! Пригласи ещё 4-х людей и ты получишь полный доступ ко всем курсам НАВСЕГДА!')
            if ref[3] == 4:
                bot.send_message(ref[0], f'Поздравляю! Ровно 5 пользователей перешли по твоей реферальной ссылке и купили у нас курс 🎆 Ты получаешь доступ ко всем курсам НАВСЕГДА!')
                db.update_user_buy('all', ref[0])
                db.update_user_money(user[4], -1)
                bot.send_message(message.chat.id, f'Ссылка: {disk_link}', reply_markup=markup)
            db.update_user_money(user[4], ref[3] + 1)
        db.update_user_buy('all', message.chat.id)
        markup.add(home)
        bot.send_message(message.chat.id, f'Спасибо за покупку всех товаров!\nСсылка: {disk_link}', reply_markup=markup)

bot.infinity_polling(skip_pending = True)
