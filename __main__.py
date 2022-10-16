import requests
import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
flag = True


@bot.message_handler(commands=['start'])
def welcome(message):
    stick = open('stickers/welcome.webp', 'rb')
    bot.send_sticker(message.chat.id, stick)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Сейчас")
    item2 = types.KeyboardButton("Прогноз на...")

    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     'Привет, <b>{0.first_name}</b>!\nЯ могу подсказать тебе погоду в любой точке мира. Только скажи, на сколько дней ты хочешь получить прогноз !'.format(
                         message.from_user),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_weather_info(message):
    global flag
    if message.text == 'Сейчас':
        flag = True
        bot.send_message(message.chat.id, 'В каком городе ты хочешь узнать погоду?')
    elif message.text == 'Прогноз на...':
        bot.send_message(message.chat.id, 'В каком городе ты хочешь узнать погоду? Во сколько часов?')
        flag = False
    else:
        stick = open('stickers/funny_delay.webp', 'rb')
        bot.send_sticker(message.chat.id, stick)
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton("Thanks <3", callback_data='good')
        item2 = types.InlineKeyboardButton("://", callback_data='bad')

        markup.add(item1, item2)
        if flag:
            bot.send_message(message.chat.id, get_current_weather(message.text.split(sep=',. ')[0]),
                             reply_markup=markup)
        else:
            city, hour = message.text.split(sep=', ')
            hour = hour.split(sep='.')[0]
            bot.send_message(message.chat.id, get_weather_forecast(city, hour), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data == 'good':
            bot.send_message(call.message.chat.id, 'Нет проблем! 😊')
        else:
            bot.send_message(call.message.chat.id, 'Почему ты так со мной, человек.. 😢')
    # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Thanks <3',
    #                       reply_markup=None)

    # bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
    #                           text="It is test notice!!11")
    except Exception as e:
        print(repr(e))


def get_current_weather(city):
    config.params['q'] = city
    res = requests.get(config.current_url, params=config.params)
    if res.status_code == 200:
        data = res.json()['current']
        template = 'Температура в городе {} сейчас --  {}°C. {}. Давление - {} мм.рт.ст. Скорость ветра - {} м/с'
        return template.format(city, data["temp_c"], data["condition"]['text'],
                               str(int(float(data['pressure_mb']) * 0.750062)),
                               str(int(float(data['wind_kph']) * 0.277)))
    else:
        return 'Город не обнаружен :('


def get_weather_forecast(city, hour):
    config.params['q'] = city
    config.params['hour'] = hour
    res = requests.get(config.forecast_url, params=config.params)

    if res.status_code == 200:
        data = res.json()['forecast']['forecastday'][0]['hour'][0]
        city = city[0: -1] + 'e'
        template = '{} в {} ожидается {} °C. {}. Давление - {} мм.рт.ст. Скорость ветра - {} м/с'
        return template.format(data['time'], city, data["temp_c"], data["condition"]['text'],
                               str(int(float(data['pressure_mb']) * 0.750062)),
                               str(int(float(data['wind_kph']) * 0.277)))
    else:
        return 'Не верно введены город или время :('


bot.polling(none_stop=True)
