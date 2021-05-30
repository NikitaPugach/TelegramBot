from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import sqlite3
import telebot
import os


bot = telebot.TeleBot('1865346655:AAE19x7hEmexrNL8WsxDW9g_MXjbMRXsuLA')


class UserSatate:
    def __init__(self):
        self.dict = {}

    # def create_db(self):
    #     self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_state (chat_id integer not null primary key,
    #                     dstate integer);""")
    #     self.conn.commit()

        # states = [(1, "TYPE"), (2, "FROM_PRICE"), (3, "TO_PRICE"), (4, "TRANSMISSION"), (5, "DRIVE"),
        #           (6, "MARK"), (7, "PATROL")]

    def get_current_state(self, chat_id):
        return self.dict.get(chat_id)

    def set_state(self, chat_id, state):
        data = {chat_id: state}
        self.dict.update(data)


user_state = UserSatate()
users_answers = []


def get_user_answer_index(chat_id):
    for i in range(len(users_answers)):
        if users_answers[i].chat_id == chat_id:
            return i
    return -1

# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.send_message(message.chat.id, "Привет, это бот для подбора авто. Ответь на несколько вопросов и "
                                      "мы подберем тебе машину:")
    bot.send_message(message.chat.id, "Какой тип машины Вы бы хотели?")
    bot.send_message(message.chat.id, "Нажми 1 если Седан")
    bot.send_message(message.chat.id, "Нажми 2 если Купе")
    bot.send_message(message.chat.id, "Нажми 3 если Кроссовер")
    bot.send_message(message.chat.id, "Нажми 4 если Внедорожник")

    # keyboard = types.InlineKeyboardMarkup()
    # url_button = types.InlineKeyboardButton(text="Перейти на Яндекс", url="https://ya.ru")
    # keyboard.add(url_button)

    answer = UserAnswerData(message.chat.id)
    index = get_user_answer_index(message.chat.id)
    if index != -1:
        users_answers[index] = answer
    else:
        users_answers.append(answer)

    user_state.set_state(message.chat.id, 1)


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Ответь на несколько вопросов:")
    bot.send_message(message.chat.id, "Какой тип машины Вы бы хотели?")
    bot.send_message(message.chat.id, "Нажми 1 если Седан")
    bot.send_message(message.chat.id, "Нажми 2 если Купе")
    bot.send_message(message.chat.id, "Нажми 3 если Кроссовер")
    bot.send_message(message.chat.id, "Нажми 4 если Внедорожник")

    answer = UserAnswerData(message.chat.id)
    index = get_user_answer_index(message.chat.id)
    if index != -1:
        users_answers[index] = answer
    else:
        users_answers.append(answer)

    user_state.set_state(message.chat.id, 1)


@bot.message_handler(func=lambda message: user_state.get_current_state(message.chat.id) == 1)
def user_entering_type(message):
    if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    if int(message.text) < 1 or int(message.text) > 4:
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    index = get_user_answer_index(message.chat.id)
    users_answers[index].type = int(message.text)

    bot.send_message(message.chat.id, "Какая минимальная цена машины в долларах?")
    user_state.set_state(message.chat.id, 2)


@bot.message_handler(func=lambda message: user_state.get_current_state(message.chat.id) == 2)
def user_entering_from_price(message):
    if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    index = get_user_answer_index(message.chat.id)
    users_answers[index].from_price = int(message.text)

    bot.send_message(message.chat.id, "Какая максимальная цена машины в долларах?")
    user_state.set_state(message.chat.id, 3)


@bot.message_handler(func=lambda message: user_state.get_current_state(message.chat.id) == 3)
def user_entering_to_price(message):
    if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    index = get_user_answer_index(message.chat.id)
    users_answers[index].to_price = int(message.text)

    bot.send_message(message.chat.id, "Тип коробки передач:")
    bot.send_message(message.chat.id, "0 - Любая")
    bot.send_message(message.chat.id, "1 - Автоматическая")
    bot.send_message(message.chat.id, "2 - Механическая")
    user_state.set_state(message.chat.id, 4)


@bot.message_handler(func=lambda message: user_state.get_current_state(message.chat.id) == 4)
def user_entering_transmission(message):
    if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    if int(message.text) < 0 or int(message.text) > 2:
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    index = get_user_answer_index(message.chat.id)
    users_answers[index].transmission = int(message.text)

    bot.send_message(message.chat.id, "Привод:")
    bot.send_message(message.chat.id, "0 - Любой")
    bot.send_message(message.chat.id, "1 - 2х2")
    bot.send_message(message.chat.id, "2 - 4х4")
    user_state.set_state(message.chat.id, 5)


@bot.message_handler(func=lambda message: user_state.get_current_state(message.chat.id) == 5)
def user_entering_drive(message):
    if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    if int(message.text) < 0 or int(message.text) > 2:
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    index = get_user_answer_index(message.chat.id)
    users_answers[index].drive = int(message.text)

    bot.send_message(message.chat.id, "Введите марку:")
    bot.send_message(message.chat.id, "0 - Любая")
    bot.send_message(message.chat.id, "1 - Skoda")
    bot.send_message(message.chat.id, "2 - Volkswagen")
    bot.send_message(message.chat.id, "3 - Audi")
    bot.send_message(message.chat.id, "4 - BMW"),
    bot.send_message(message.chat.id, "5 - Mercedes")
    bot.send_message(message.chat.id, "6 - Seat")
    bot.send_message(message.chat.id, "7 - Toyota")
    bot.send_message(message.chat.id, "8 - Suzuki")

    user_state.set_state(message.chat.id, 6)


@bot.message_handler(func=lambda message: user_state.get_current_state(message.chat.id) == 6)
def user_entering_mark(message):
    if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    if int(message.text) < 0 or int(message.text) > 8:
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    index = get_user_answer_index(message.chat.id)
    users_answers[index].mark = int(message.text)

    bot.send_message(message.chat.id, "Введите тип топлива:")
    bot.send_message(message.chat.id, "0 - Любой")
    bot.send_message(message.chat.id, "1 - Бензин")
    bot.send_message(message.chat.id, "2 - Дизель")
    user_state.set_state(message.chat.id, 7)


@bot.message_handler(func=lambda message: user_state.get_current_state(message.chat.id) == 7)
def user_entering_mark(message):
    if not message.text.isdigit():
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    if int(message.text) < 0 or int(message.text) > 2:
        # Состояние не меняем, поэтому только выводим сообщение об ошибке и ждём дальше
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return

    index = get_user_answer_index(message.chat.id)
    users_answers[index].patrol = int(message.text)

    car_data = CarData()
    results = car_data.search(users_answers[index])

    for r in results:
        bot.send_message(message.chat.id, r)

    if len(results) == 0:
        bot.send_message(message.chat.id, "К сожалению не удалось найти авто подходящее под ваш запрос.")

    bot.send_message(message.chat.id, "Нажмите '/reset', чтобы начать сначала.")

    user_state.set_state(message.chat.id, 7)


class UserAnswerData:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.type = 0
        self.from_price = 0
        self.to_price = 0
        self.transmission = 0
        self.drive = 0
        self.mark = 0
        self.patrol = 0


class CarData:
    def __init__(self):
        db_path = "data.db"
        if os.path.exists(db_path):
            os.remove(db_path)
        self.conn = sqlite3.connect("data.db")
        self.cursor = self.conn.cursor()

    def create_db(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS auto_type (id integer not null primary key, type text);""")
        self.conn.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS auto_mark (id integer not null primary key, mark text);""")
        self.conn.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS auto 
        (id integer not null primary key, mark int not null, name text,
        price integer not null, transmission boolean not null, 
        drive boolean not null, type integer not null, valume real not null, Oil boolean, salon_id integer not null);""")
        self.conn.commit()
        # transmission (true - auto, false - hand)
        # drive (true - 4x4, false - 2x2)
        # oil (true - petrol, false - diesel)

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS salon
        (id integer not null primary key, salon_name text not null, adress text not null)""")
        self.conn.commit()

        salons = [(1, "Volkswagen Auto Concern Salon", "Плехановская 117"), (2, "BMW Motors", "Гагарина 234"),
                  (3, "Mercedes Auto Salon", "Московский 209"), (4, "Japan Cars", "Клочковская 87")]
        self.cursor.executemany("INSERT INTO salon VALUES(?, ?, ?);", salons)

        types = [(1, 'sedan'), (2, 'coope'), (3, 'crossover'), (4, 'outlander')]
        self.cursor.executemany("INSERT INTO auto_type VALUES(?, ?);", types)
        self.conn.commit()

        marks = [(1, 'Skoda'), (2, 'Volkswagen'), (3, 'Audi'), (4, 'BMW'),
                 (5, 'Mercedes'), (6, 'Seat'), (7, 'Toyota'), (8, 'Suzuki')]
        self.cursor.executemany("INSERT INTO auto_mark VALUES(?, ?);", marks)
        self.conn.commit()

        autos = [(1, 1, 'Octavia', 27000, True, False, 1, 2.0, True, 1),
                 (2, 1, 'Octavia', 24000, False, False, 1, 1.8, True, 1),
                 (3, 1, 'Kadiaq', 34000, True, True, 3, 2.8, False, 1),
                 (4, 1, 'Kadiaq', 33000, True, False, 3, 2.3, True, 1),
                 (5, 2, 'Polo', 13000, False, False, 1, 1.2, True, 1),
                 (6, 2, 'Passat', 37000, True, False, 1, 2.6, True, 1),
                 (7, 2, 'Touareg', 57000, True, True, 3, 3.2, False, 1),
                 (8, 3, 'TT', 43000, True, False, 2, 2.7, True, 1),
                 (9, 3, 'Q7', 67000, True, True, 3, 4.0, False, 1),
                 (10, 3, 'A3', 37000, True, False, 1, 2.8, True, 1),
                 (11, 4, 'X5', 64000, True, True, 3, 4.1, False, 2),
                 (12, 4, 'M1', 34000, True, False, 2, 2.3, True, 2),
                 (13, 4, '6 series', 47000, True, True, 2, 2.9, False, 2),
                 (14, 5, 'G-Class', 105000, True, True, 4, 4.5, False, 3),
                 (15, 5, 'GLE', 67000, True, True, 3, 3.6, True, 3),
                 (16, 5, 'E-Class', 89000, True, True, 1, 4.0, False, 3),
                 (17, 6, 'Ateca', 32000, True, False, 3, 2.1, True, 1),
                 (18, 6, 'Ibiza', 17000, False, False, 2, 1.4, True, 1),
                 (19, 6, 'Arona', 23000, False, False, 2, 1.7, True, 1),
                 (20, 7, 'Camry', 30000, True, False, 1, 2.2, True, 4),
                 (21, 7, 'C-HR', 29000, True, False, 2, 1.7, True, 4),
                 (22, 7, 'Land Cruiser 200', 57000, True, True, 4, 4.2, False, 4),
                 (23, 7, 'RAV4', 37000, True, True, 3, 2.3, True, 4),
                 (24, 8, 'Jimny', 24000, False, True, 4, 1.5, True, 4),
                 (25, 8, 'Vitara', 18000, False, False, 3, 1.4, True, 4),
                 (26, 8, 'SX4', 20000, False, False, 3, 1.6, True, 4),
                 ]
        self.cursor.executemany("INSERT INTO auto VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", autos)
        self.conn.commit()

    def create_query(self, data: UserAnswerData):
        query = "SELECT auto_mark.mark, name, price, transmission, drive, auto_type.type, valume, oil, salon_id " \
                "FROM auto inner join auto_mark on auto.mark = auto_mark.id " \
                "inner join auto_type on auto.type = auto_type.id "

        if data.type == 1:
            query += "Where auto_type.id = 1 "
        elif data.type == 2:
            query += "Where auto_type.id = 2 "
        elif data.type == 3:
            query += "Where auto_type.id = 3 "
        elif data.type == 4:
            query += "Where auto_type.id = 4 "

        if not data.from_price >= data.to_price:
            query += f"AND price BETWEEN {data.from_price} AND {data.to_price} "

        if data.transmission == 1:
            query += f"AND transmission = 1 "
        elif data.transmission == 2:
            query += f"AND transmission = 0 "

        if data.drive == 2:
            query += "AND drive = 1 "
        elif data.drive == 1:
            query += "AND drive = 0 "

        if data.mark > 0:
            query += f"AND auto_mark.id = {data.mark} "

        if data.patrol == 1:
            query += "AND Oil = 1 "
        elif data.patrol == 2:
            query += "AND Oil = 0"

        return query

    def search(self, data: UserAnswerData):
        self.create_db()
        query = self.create_query(data)
        print(query)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        autos = []
        for r in results:
            autos.append(Auto(r))

        self.cursor.execute("""SELECT id, salon_name, adress FROM salon""")
        results = self.cursor.fetchall()
        salons = []
        for r in results:
            salons.append(Salon(r))
        for auto in autos:
            salons[auto.salon - 1].add_auto(auto)

        result_strings = []

        for salon in salons:
            if not len(salon.autos) == 0:
                result_strings.append(str(salon))
                for auto in salon.autos:
                    result_strings.append(str(auto))

        return result_strings


class Auto:
    def __init__(self, data):
        self.mark = data[0]
        self.name = data[1]
        self.price = data[2]
        self.transmission = data[3]
        self.drive = data[4]
        self.type = data[5]
        self.valume = data[6]
        self.oil = data[7]
        self.salon = data[8]

    def __str__(self):
        str = f"  {self.mark} {self.name} {self.valume}L {self.price}$, "
        if self.oil:
            str += "Patrol, "
        else:
            str += "Diesel, "
        if self.transmission:
            str += "Auto transmission, "
        else:
            str += "Manual transmission, "
        if self.drive:
            str += "4x4"
        else:
            str += "2x2"

        return str


class Salon:
    def __init__(self, data):
        self.id = data[0]
        self.name = data[1]
        self.adress = data[2]
        self.autos = []

    def __str__(self):
        return f"\"{self.name}\" Адресс: {self.adress}"

    def add_auto(self, auto: Auto):
        self.autos.append(auto)


if __name__ == '__main__':
    bot.polling(none_stop=True)