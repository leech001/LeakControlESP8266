# -*- coding: utf-8 -*-
import time
import telepot
import paho.mqtt.client as mqtt

from telepot.namedtuple import ReplyKeyboardMarkup

token = '434888669:AAH6ioqBIgUmDH3dRGz6qLpzMz0_g_wknuA$'  # Waterbot
bot = telepot.Bot(token)
g_chat_id = 65963379

w_topic = 'bath/+/water/'


# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))


def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    if msg.payload == 'yes':
        if 'small' in msg.topic:
            bot.sendMessage(g_chat_id, 'Внимание протечка в маленькой ванне! Закрываем краны!')
            time.sleep(60)

        elif 'big' in msg.topic:
            bot.sendMessage(g_chat_id, 'Внимание протечка в большой ванне! Закрываем краны!')
            time.sleep(60)


def on_publish(client, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(client, obj, level, string):
    print(string)


mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Connect
mqttc.username_pw_set('user', '#private!')
mqttc.connect('192.168.0.21', 1883)

# Start subscribe, with QoS level 0
mqttc.subscribe(w_topic, 0)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        command = msg['text']
        if command == '/start' or command == '/start@LeechDacha_bot':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Инфо'), dict(text='Маленькая ванная'), dict(text='Большая ванная')]
            ], resize_keyboard=True)
            bot.sendMessage(chat_id, 'Привет! Я бот слежения за утечками. Выбери раздел', reply_markup=markup)

        elif command == 'Главное меню':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Инфо'), dict(text='Маленькая ванная'), dict(text='Большая ванная')]
            ], resize_keyboard=True)
            bot.sendMessage(chat_id, 'Выбери раздел', reply_markup=markup)

        elif command == u'Инфо':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Главное меню')],
            ], resize_keyboard=True)
            bot.sendMessage(chat_id, 'Выбери объект', reply_markup=markup)

        elif command == u'Маленькая ванная':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Закрыть краны (м)'), dict(text='Открыть краны (м)')],
                [dict(text='Закрыть горячую (м)'), dict(text='Закрыть холодную (м)')],
                [dict(text='Открыть горячую (м)'), dict(text='Открыть холодную (м)')],
                [dict(text='Главное меню')],
            ], resize_keyboard=True)
            bot.sendMessage(chat_id, 'Управление маленькой ванной. Выбери задачу', reply_markup=markup)

        elif command == u'Закрыть краны (м)':
            mqttc.publish('bath/small/tap/cold/', 'close')
            mqttc.publish('bath/small/tap/hot/', 'close')
            bot.sendMessage(chat_id, 'Краны закрыты')

        elif command == u'Открыть краны (м)':
            mqttc.publish('bath/small/tap/cold/', 'open')
            mqttc.publish('bath/small/tap/hot/', 'open')
            bot.sendMessage(chat_id, 'Краны открыты')

        elif command == u'Закрыть горячую (м)':
            mqttc.publish('bath/small/tap/hot/', 'close')
            bot.sendMessage(chat_id, 'Кран горячей воды закрыт')

        elif command == u'Закрыть холодную (м)':
            mqttc.publish('bath/small/tap/cold/', 'close')
            bot.sendMessage(chat_id, 'Кран холодной воды закрыт')

        elif command == u'Открыть горячую (м)':
            mqttc.publish('bath/small/tap/hot/', 'open')
            bot.sendMessage(chat_id, 'Кран горячей воды открыт')
            bot.sendMessage(chat_id, 'Кран холодной воды открыт')

        elif command == u'Открыть холодную (м)':
            mqttc.publish('bath/small/tap/cold/', 'open')

        elif command == u'Большая ванная':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Закрыть краны (б)'), dict(text='Открыть краны (б)')],
                [dict(text='Закрыть горячую (б)'), dict(text='Закрыть холодную (б)')],
                [dict(text='Открыть горячую (б)'), dict(text='Открыть холодную (б)')],
                [dict(text='Главное меню')],
            ], resize_keyboard=True)
            bot.sendMessage(chat_id, 'Управление большой ванной. Выбери задачу', reply_markup=markup)

        elif command == u'Закрыть краны (б)':
            mqttc.publish('bath/big/tap/cold/', 'close')
            mqttc.publish('bath/big/tap/hot/', 'close')
            bot.sendMessage(chat_id, 'Краны закрыты')

        elif command == u'Открыть краны (б)':
            mqttc.publish('bath/big/tap/cold/', 'open')
            mqttc.publish('bath/big/tap/hot/', 'open')
            bot.sendMessage(chat_id, 'Краны открыты')

        elif command == u'Закрыть горячую (б)':
            mqttc.publish('bath/big/tap/hot/', 'close')
            bot.sendMessage(chat_id, 'Кран горячей воды закрыт')

        elif command == u'Закрыть холодную (б)':
            mqttc.publish('bath/big/tap/cold/', 'close')
            bot.sendMessage(chat_id, 'Кран холодной воды закрыт')

        elif command == u'Открыть горячую (б)':
            mqttc.publish('bath/big/tap/hot/', 'open')
            bot.sendMessage(chat_id, 'Кран горячей воды открыт')

        elif command == u'Открыть холодную (б)':
            mqttc.publish('bath/big/tap/cold/', 'open')
            bot.sendMessage(chat_id, 'Кран холодной воды открыт')


bot.message_loop({'chat': on_chat_message})
print('Listening ...')

while 1:
    mqttc.loop()