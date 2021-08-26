import os
from sqlalchemy.sql.functions import count
from sqlalchemy.orm import scoped_session
import telebot
from telebot import types
from weather import getCurrentWeather
from time import sleep
import models
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)
SQLsession = SessionLocal()



TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


bot = telebot.TeleBot(TOKEN, parse_mode=None)

def defaultMarkup():
    markup = types.ReplyKeyboardMarkup()
    
    item_help = types.KeyboardButton('/help')
    item_city = types.KeyboardButton('/city')
    item_weather = types.KeyboardButton('/weather')
    
    markup.row(item_help, item_city)
    markup.row(item_weather)

    return markup


def addToDatabase(tel_id, country, city):
    new_user = models.User(telegram_id=tel_id, country=country, city=city)

    SQLsession.add(new_user)
    SQLsession.commit()


def updateCountry(tel_id, country):
    user = (SQLsession.query(models.User)
        .filter_by(telegram_id=tel_id)
        .first())
    user.country = country

    SQLsession.commit()


def updateCity(tel_id, city):
    user = (SQLsession.query(models.User)
        .filter_by(telegram_id=tel_id)
        .first())
    user.city = city

    SQLsession.commit()


def deleteUser(tel_id):
    user = (SQLsession.query(models.User)
        .filter_by(telegram_id=tel_id)
        .first())
    user.delete()

    SQLsession.commit()


@bot.message_handler(commands=['start', 'старт'])
def send_start(message):

    is_registered = (SQLsession.query(models.User)
        .filter_by(telegram_id = message.chat.id)
        .first())

    if is_registered is not None:
        bot.send_message(message.chat.id, "Вы уже зарегестрированы", reply_markup=defaultMarkup())
    else:
        reply = """
Что бы начать, выберете свою страну и город
Позже вы сможете их изменить

<b>Введите страну</b>
        """
        msg = bot.send_message(message.chat.id, reply, parse_mode='HTML')
        addToDatabase(message.chat.id, 'None', 'None')

        bot.register_next_step_handler(msg, process_country_step)


def process_country_step(message):
    try:
        country = str(message.text)

        updateCountry(message.chat.id, country)

        msg = bot.reply_to(message, "<b>Введите город</b>", parse_mode="HTML",)
        bot.register_next_step_handler(msg, process_city_step)
    except Exception as e:
        bot.send_message(message.chat.id, """
Упс... Что-то пошло не так, возможно поможет изменение города или страны
<b>Через команду /city</b>
""", reply_markup=defaultMarkup(), parse_mode='HTML')


def process_city_step(message):
    try:
        city = str(message.text)

        updateCity(message.chat.id, city)

        current_user = (SQLsession.query(models.User)
            .filter_by(telegram_id=message.chat.id)
            .first())

        reply = f"""
Все готово!

Ваши страна и город: <i>{current_user.country}, {current_user.city}</i>

Для получение нынешней погоды введите /погода или /weather
Для изменения города введите /город /city
        """
        bot.send_message(message.chat.id, reply, parse_mode="HTML", reply_markup=defaultMarkup())
    except Exception as e:
        bot.reply_to(message, """
Упс... Что-то пошло не так, возможно поможет изменение города или страны
<b>Через команду /city</b>
""", reply_markup=defaultMarkup(), parse_mode='HTML', )


@bot.message_handler(commands=['help', 'помощь'])
def send_help(message):

    is_registered = (SQLsession.query(models.User)
        .filter_by(telegram_id = message.chat.id)
        .first() is not None)

    if is_registered:
        reply = """
Для получение нынешней погоды введите /погода или /weather
Для изменения города введите /город или /city
"""
        bot.send_message(message.chat.id, reply, reply_markup=defaultMarkup())
    else:
        reply = """
Вы пока что не ввели погоду какого города хотите получать
Напишите /старт или /start, что бы начать
"""
        bot.send_message(message.chat.id, reply)



@bot.message_handler(commands=['погода', 'weather'])
def send_weather(message):


    is_registered = (SQLsession.query(models.User)
        .filter_by(telegram_id = message.chat.id)
        .first() is not None)
    
    if is_registered:
        user = (SQLsession.query(models.User)
            .filter_by(telegram_id=message.chat.id)
            .first())

        country = user.country
        city = user.city

        try:
            reply = getCurrentWeather(country, city)
        except Exception as e:
            reply = """
Упс... Что-то пошло не так, возможно поможет изменение города или страны
<b>Через команду /city</b>
            """
        bot.send_message(message.chat.id, reply, parse_mode="HTML", reply_markup=defaultMarkup())
    else:
        reply = """
Вы пока что не ввели погоду какого города хотите получать
Напишите /старт или /start, что бы начать
"""
        bot.send_message(message.chat.id, reply, parse_mode="HTML")



@bot.message_handler(commands=['город', 'city'])
def change_city(message):
    is_registered = (SQLsession.query(models.User)
        .filter_by(telegram_id = message.chat.id)
        .first() is not None)
    
    if is_registered:
        user = (SQLsession.query(models.User)
                .filter_by(telegram_id=message.chat.id)
                .first())

        country = user.country
        city = user.city

        bot.send_message(message.chat.id, f"Ваши нынешние данные: <i>{country}, {city}</i>", parse_mode='HTML')
        msg = bot.send_message(message.chat.id, "<b>Введите страну</b>", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_country_step)
    else:
        reply = """
Вы пока что не зарегестрированы
Напишите /старт или /start, что бы начать
"""
        bot.send_message(message.chat.id, reply, parse_mode="HTML")



bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

print('STARTED')
bot.polling(none_stop=True)