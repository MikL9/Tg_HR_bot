import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telebot import types
import mysql.connector

bot_token = '5114314620:AAHL9cGCVcN1b7e9Vsax0hHKJoDN8g6UKZo'
bot = telebot.TeleBot(bot_token)

user = bot.get_me()

# database
host = 'localhost'
database = 'pmi_staff-test'
db_user = 'pavel'
db_pass = '8e8d3RtRfM'

photo_list = []
photo_type = ''
edit_photos = 0
path = '/var/www/pmihrbot/files/tgtemplates/'
zakon = '''Соглашение на обработку персональных данных

1. Принимая условия настоящего Соглашения, 
пользователь даёт своё согласие @pmi_staff_bot (далее — Компания) на сбор, 
хранение и обработку своих персональных данных, переданных через приложение 
для обмена сообщениями Telegram путем отправки простых текстовых сообщений 
и фото. Под персональными данными понимается любая информация, относящаяся 
к прямо или косвенно определённому, или определяемому физическому лицу 
(гражданину).
Пользователь:
• подтверждает, что все указанные им данные принадлежат лично ему;
• подтверждает и признает, что им внимательно в полном объеме прочитано 
Соглашение и условия обработки его персональных данных, переданных через приложение, 
текст Соглашения и условия обработки персональных данных ему понятны;
• выражает Согласие на обработку персональных данных без оговорок и 
ограничений (далее – Согласие). Моментом принятия Согласия является нажатие на 
кнопку "Согласен" в конце Соглашения;
• подтверждает, что, давая Согласие, он действует свободно, 
своей волей и в своем интересе;
2.  Основанием для обработки персональных данных являются: статья 24 
Конституции РФ и статья 6 Федерального закона № 152-ФЗ «О персональных данных» 
с дополнениями и изменениями.
3. В ходе обработки с персональными данными будут совершены следующие операции: 
сбор, хранение, уточнение, передача, блокирование, удаление, уничтожение.
4. Компания обязуется не передавать полученную от Пользователя информацию 
третьим лицам. Не считается нарушением предоставление персональных данных третьим лицам, 
действующим на основании договора с Компанией, для исполнения обязательств перед 
Пользователем и только в рамках настоящего Соглашения.
5. Персональные данные хранятся и обрабатываются до завершения всех необходимых 
процедур либо до ликвидации Компании.
6. Компания при обработке персональных данных принимает необходимые и достаточные 
организационные и технические меры для защиты персональных данных от неправомерного 
доступа к ним, а также от иных неправомерных действий в отношении персональных данных.'''
warning = '''Обращаю Ваше внимание, что снимок документа необходимо прикрепить как фото, а не как файл.'''


# main_menu_keyboard = telebot.types.ReplyKeyboardMarkup(True)
# main_menu_keyboard.add('test1')
# @bot.message_handler(commands=['start', 'help'])
# def send_welcome(message):
#   bot.reply_to(message, welcome_message, reply_markup=main_menu_keyboard)


def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Устроиться на работу", callback_data="cb_yes"),
               InlineKeyboardButton("Выход", callback_data="cb_no"))
    return markup


def gen_markup_docs():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Да", callback_data="cb_yes_docs"),
               InlineKeyboardButton("Выход", callback_data="cb_no"))
    return markup


def gen_markup_approve(step):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    if step == 1:
        markup.add(InlineKeyboardButton("Согласен", callback_data="cb_yes_approve"),
                   InlineKeyboardButton("Ознакомиться", callback_data="cb_zakon_info"),
                   InlineKeyboardButton("Выход", callback_data="cb_no"))
    elif step == 2:
        markup.add(InlineKeyboardButton("Согласен", callback_data="cb_yes_approve"),
                   InlineKeyboardButton("Выход", callback_data="cb_no"))
    return markup


@bot.message_handler(commands=['start'])
def phone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Подтвердить номер", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id,
                     '''Добрый день, меня зовут MikL9.
Вы попали в виртуальный отдел кадров. Я помогу Вам подготовить документы для передачи в отдел кадров.
Для продолжения, пожалуйста, отправьте свой номер телефона и я заскамлю вас.
Для этого нажмите кнопку "Подтвердить номер".''',
                     reply_markup=keyboard)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        print(message.contact)
        keyboard = types.ReplyKeyboardRemove()
        init_into_table(message.contact)
        bot.send_message(message.chat.id, 'Спасибо! Вход успешно выполнен.', reply_markup=keyboard)
        message_start_approve(message)


def message_start_approve(message):
    bot.send_message(message.chat.id,
                     '''Перед тем как перейти к подготовке документов, мне необходимо Ваше согласие на обработку, хранение и использование Ваших персональных данных на основании ФЗ № 152-ФЗ «О персональных данных» от 27.07.2006 г.''',
                     reply_markup=gen_markup_approve(1))


def start_document_action(message):
    bot.send_message(message.chat.id,
                     '''Приготовьте, пожалуйста, следующие документы:
- Паспорт(2-3 страницы)
- Паспорт(4-5 страницы)
- Паспорт(6-7 страницы)
- Паспорт(18-19 страницы)
- Текущие личные банковские реквизиты (Наименование банка, БИК, Р/С, ФИО полностью)
- СНИЛС
- Заявление о приеме''')
    bot.send_message(message.chat.id, "Все ли документы у Вас в наличии? : ", reply_markup=gen_markup_docs())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global photo_type
    global edit_photos
    global warning
    if call.data == "edit_photos":
        bot.answer_callback_query(call.id, "Lets edit")
        edit_photos = 1
        start_document_action(call.message)
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Answer is Yes")
        start_document_action(call.message)
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")
        bot.send_message(call.message.chat.id, 'Процесс завершен.')
        photo_type = ''
        phone(call.message)
    elif call.data == "cb_zakon_info":
        bot.answer_callback_query(call.id, "Answer is ShowInfo")
        bot.send_message(call.message.chat.id,
                         zakon, reply_markup=gen_markup_approve(2))
    elif call.data == "cb_yes_approve":
        bot.answer_callback_query(call.id, "Answer is Approve")
        bot.send_message(call.message.chat.id, "Итак, давайте решим, что Вам нужно : ", reply_markup=gen_markup())
    elif call.data == "cb_yes_docs":
        bot.answer_callback_query(call.id, "Answer is YesDocs")
        send_passport1(call.message)


def send_passport1(message):
    global photo_type
    global warning
    global path
    bot.send_message(message.chat.id,
                     '''Начнём с паспорта.
Обратите, пожалуйста, внимание, что фото должно быть без бликов и посторонних предметов.''')
    passport = open(path + 'passport1.jpg', 'rb')
    bot.send_photo(message.chat.id, passport,
                   caption='''Посмотрите, пожалуйста, как выглядит образец фото докумета Паспорт(2-3 страницы)
    Прикрепите, пожалуйста, фото документа Паспорт(2-3 страницы) согласно образцу''')
    bot.send_message(message.chat.id, warning)
    photo_type = 'passport1'


def after_passport1(message, type):
    global photo_type
    global path
    if type == 'passport2':
        template = open(path + 'passport2.jpg', 'rb')
        bot.send_photo(message.chat.id, template,
                       caption='''Посмотрите, пожалуйста, как выглядит образец фото докумета Паспорт(4-5 страницы)
Прикрепите, пожалуйста, фото документа Паспорт(4-5 страницы) согласно образцу''')
        bot.send_message(message.chat.id, warning)
        photo_type = type
    if type == 'passport3':
        template = open(path + 'passport3.jpg', 'rb')
        bot.send_photo(message.chat.id, template,
                       caption='''Посмотрите, пожалуйста, как выглядит образец фото докумета Паспорт(6-7 страницы)
Прикрепите, пожалуйста, фото документа Паспорт(6-7 страницы) согласно образцу''')
        bot.send_message(message.chat.id, warning)
        photo_type = type
    if type == 'passport7':
        template = open(path + 'passport7.jpg', 'rb')
        bot.send_photo(message.chat.id, template,
                       caption='''Посмотрите, пожалуйста, как выглядит образец фото докумета Паспорт(18-19 страницы)
Прикрепите, пожалуйста, фото документа Паспорт(18-19 страницы) согласно образцу''')
        bot.send_message(message.chat.id, warning)
        photo_type = type
    if type == 'bank':
        template = open(path + 'bank.jpg', 'rb')
        bot.send_photo(message.chat.id, template,
                       caption='''Посмотрите, пожалуйста, как выглядит образец фото докумета Текущие личные банковские реквизиты 
Прикрепите, пожалуйста, фото документа Текущие личные банковские реквизиты  согласно образцу''')
        bot.send_message(message.chat.id, warning)
        photo_type = type
    if type == 'snils':
        template = open(path + 'snils.jpg', 'rb')
        bot.send_photo(message.chat.id, template,
                       caption='''Посмотрите, пожалуйста, как выглядит образец фото докумета СНИЛС
Прикрепите, пожалуйста, фото документа СНИЛС согласно образцу''')
        bot.send_message(message.chat.id, warning)
        photo_type = type
    if type == 'zayava':
        bot.send_message(message.chat.id, '''Прикрепите, пожалуйста, фото Заявления о приеме''')
        bot.send_message(message.chat.id, warning)
        photo_type = type


@bot.message_handler(content_types=['photo'])
def get_user_pics(message):
    global photo_type
    fileid = message.photo[-1].file_id
    file_info = bot.get_file(fileid)
    downloaded_file = bot.download_file(file_info.file_path)
    dirName = '/var/www/pmi.test/lib/files/bot/' + str(message.chat.id)
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        print("Directory ", dirName, " Created ")
    else:
        print("Directory ", dirName, " already exists")
    filepath = dirName + '/' + str(message.chat.id) + 'guid' + fileid
    filename = "%s" % filepath
    if photo_type != '':
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)
        psih(message, fileid)


def psih(message, guid):
    global photo_type
    global edit_photos
    doc_type = photo_type
    if doc_type == 'passport1':
        insert_varibles_into_table(message.chat.id, doc_type, message.photo[-1].file_id, guid)
        photo_type = 'passport2'
        after_passport1(message, photo_type)
    if doc_type == 'passport2':
        insert_varibles_into_table(message.chat.id, doc_type, message.photo[-1].file_id, guid)
        photo_type = 'passport3'
        after_passport1(message, photo_type)
    if doc_type == 'passport3':
        insert_varibles_into_table(message.chat.id, doc_type, message.photo[-1].file_id, guid)
        photo_type = 'passport7'
        after_passport1(message, photo_type)
    if doc_type == 'passport7':
        insert_varibles_into_table(message.chat.id, doc_type, message.photo[-1].file_id, guid)
        photo_type = 'bank'
        after_passport1(message, photo_type)
    if doc_type == 'bank':
        insert_varibles_into_table(message.chat.id, doc_type, message.photo[-1].file_id, guid)
        photo_type = 'snils'
        after_passport1(message, photo_type)
    if doc_type == 'snils':
        insert_varibles_into_table(message.chat.id, doc_type, message.photo[-1].file_id, guid)
        photo_type = 'zayava'
        after_passport1(message, photo_type)
    if doc_type == 'zayava':
        insert_varibles_into_table(message.chat.id, doc_type, message.photo[-1].file_id, guid)
        if edit_photos == 1:
            set_checked_default(message.chat.id)
        bot.send_message(message.chat.id, '''Отлично! Ваши документы приняты!''')
        bot.send_message(message.chat.id, '''Внимание! Просьба не удалять и не блокировать бота.
В случае, если ваши фотографии не пройдут проверку, мы попросим вас выслать некоторые документы заново. Спасибо!''')
        photo_type = ''


def insert_varibles_into_table(user_id, document_id, img_id, guid):
    filepath = 'files/' + str(user_id) + 'guid' + guid
    guid = str(user_id) + 'guid' + guid
    parent_tg_id = user_id
    global connection, cursor, host, database, db_user, db_pass
    try:
        connection = mysql.connector.connect(host=host,
                                             database=database,
                                             user=db_user,
                                             password=db_pass)
        cursor = connection.cursor()

        search_staff = """SELECT id FROM staff_tg_reg WHERE user_id = {} LIMIT 1""".format(user_id)
        cursor.execute(search_staff)
        staff_data = cursor.fetchall()
        if staff_data.__len__() > 0:
            user_id = staff_data[0][0]
        else:
            print("staff_data is broken")
            return False

        search_docs = """SELECT * FROM staff_tg_doctype WHERE tpl_name = '{}' LIMIT 1""".format(document_id)
        cursor.execute(search_docs)
        docs_data = cursor.fetchall()
        if docs_data.__len__() > 0:
            document_id = docs_data[0][0]
            doc_type = docs_data[0][6]
        else:
            print("docs_data is broken")
            return False

        query_file_exist = """SELECT * FROM staff_tg_files WHERE staff_tg_id='{}' AND document_id='{}'""".format(
            user_id, document_id)
        cursor.execute(query_file_exist)
        docs_file = cursor.fetchall()
        field_names = [i[0] for i in cursor.description]
        if docs_file.__len__() > 0:
            docs_file = dict(zip(field_names, docs_file[0]))
            old_img_id = docs_file['img_id']
            mySql_update_query = "UPDATE staff_tg_files SET img_id='%s', path='%s', is_correct=0 WHERE staff_tg_id=%s AND doc_type=%s AND document_id=%s " \
                                 % (guid, filepath, user_id, doc_type, document_id)
            cursor.execute(mySql_update_query)
            connection.commit()
            print("Record Updated successfully in staff_tg_files table")

            files_update_query = "UPDATE files SET guid='%s' WHERE guid='%s'" % (guid, old_img_id)
            cursor.execute(files_update_query)
            connection.commit()
            print("Record Updated successfully in files table")
        else:
            mySql_insert_query = """INSERT INTO staff_tg_files (staff_tg_id, document_id, doc_type, img_id, path) 
                                            VALUES (%s, %s, %s, %s, %s) """

            record = (user_id, document_id, doc_type, guid, filepath)
            cursor.execute(mySql_insert_query, record)
            connection.commit()
            print("Record inserted successfully into staff_tg_files table")

            mySql_insert_files = """INSERT INTO files (guid, type, parent_tg_id) 
                                                    VALUES (%s, %s, %s) """

            record = (guid, doc_type, parent_tg_id)
            cursor.execute(mySql_insert_files, record)
            connection.commit()
            print("Record inserted successfully into staff_tg_files table")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def init_into_table(data):
    user_id = data.user_id
    phonenumber = data.phone_number
    global connection, cursor, host, database, db_user, db_pass
    try:
        connection = mysql.connector.connect(host=host,
                                             database=database,
                                             user=db_user,
                                             password=db_pass)
        cursor = connection.cursor()

        search_reg = """SELECT * FROM staff_tg_reg WHERE user_id = {}""".format(user_id)
        cursor.execute(search_reg)
        staff_data = cursor.fetchall()
        if staff_data.__len__() > 0:
            print("staff_data is broken")
            return False

        mySql_insert_query = """INSERT INTO staff_tg_reg (user_id, phone, active) 
                                VALUES (%s, %s, 0) """

        record = (user_id, phonenumber)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        print("Record inserted successfully into staff_tg_reg table")

        cursor.execute(search_reg)
        staff_reg_id = cursor.fetchall()
        reg_id = staff_reg_id[0][0]
        print("Reg id: " + str(reg_id))

        mySql_insert_query2 = """INSERT INTO staff_tg_data (reg_id, phone, is_correct) 
                                        VALUES (%s, %s, 0) """

        record = (reg_id, phonenumber)
        cursor.execute(mySql_insert_query2, record)
        connection.commit()
        print("Record inserted successfully into staff_tg_reg table")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def set_checked_default(user_id):
    global connection, cursor, host, database, db_user, db_pass
    try:
        connection = mysql.connector.connect(host=host,
                                             database=database,
                                             user=db_user,
                                             password=db_pass)
        cursor = connection.cursor()

        cursor.execute("""UPDATE staff_tg_reg SET checked=0 WHERE user_id=%s""" % user_id)
        connection.commit()
        print("Record inserted successfully into staff_tg_reg table")

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


'''
def init_edit_photos(message):
    global photo_type
    global edit_photos
    edit_photos = 1
    if photo_type == 'passport1':
        send_passport1(message)
    else:
        after_passport1(message, photo_type)


def search_edit_photos(message):
    global connection, cursor, photo_type, host, database, db_user, db_pass
    try:
        connection = mysql.connector.connect(host=host,
                                             database=database,
                                             user=db_user,
                                             password=db_pass)
        cursor = connection.cursor()

        search_reg = """SELECT * from staff_tg_files sf
inner join staff_tg_reg sg on sg.id=sf.staff_tg_id
inner join staff_tg_doctype sdoc on sdoc.id=sf.document_id
where sg.user_id={} and sf.is_correct=0 and sg.checked=1""".format(message.chat.id)  # найти reg_id + где is_correct=0 + link tpl_name
        cursor.execute(search_reg)
        values = cursor.fetchall()
        field_names = [i[0] for i in cursor.description]
        for staff_data in values:
            staff_data = dict(zip(field_names, staff_data))
            photo_type = staff_data['tpl_name']
            init_edit_photos(message)
            wait(lambda: get_user_pics(message))

    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
'''

bot.infinity_polling()
