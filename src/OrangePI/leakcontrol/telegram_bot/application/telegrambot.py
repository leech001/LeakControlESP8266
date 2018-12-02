# -*- coding: utf-8 -*-
import asyncio
import time
import telepot
import telepot.aio
import paho.mqtt.client as mqtt
from telepot.namedtuple import ReplyKeyboardMarkup
from telepot.aio.loop import MessageLoop
import config

bot = telepot.aio.Bot(config.CONFIG['TELEGRAM_TOKEN'])
ping_iterator = 0

ping_mqtt = 0.0
ping_fail = 0
ping_device_error = 0


def on_connect(client, userdata, flags, rc):
    client.subscribe(config.CONFIG['MQTT_BOT_TOPIC'] + '#')


def on_message(client, obj, msg):
    global ping_fail
#    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if 'data/water' in msg.topic:
        notify_water(msg.topic, msg.payload)

    elif (config.CONFIG['MQTT_BOT_TOPIC'] + "state/check/mqtt") in msg.topic:
        if float(msg.payload) == ping_mqtt:
            print("MQTT pong true...")
            ping_fail = 0
        else:
            print("MQTT pong false... (%i)" % ping_fail)

    elif "big/01/state/pong" in msg.topic:
        esp_b01.pong(msg.payload)


def notify_water(topic, payload):
    if payload == b'yes':
        if 'small' in topic:
            bot.sendMessage(config.CONFIG['TELEGRAM_GROUP_CHAT_ID'],
                            'Внимание протечка в маленькой ванне! Закрываем краны!')

        elif 'big' in topic:
            bot.sendMessage(config.CONFIG['TELEGRAM_GROUP_CHAT_ID'],
                            'Внимание протечка в большой ванне! Закрываем краны!')


class EspDevice:
    def __init__(self, place, number):
        self.place = place
        self.number = number
        self.ping_packet = 0
        self.pong_packet = 0
        self.fail = False

    def ping(self, ping_packet):
        self.ping_packet = ping_packet
        self.fail = True
        mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + self.place + "/" + self.number + '/state/ping', self.ping_packet)

    def pong(self, pong_packet):
        self.pong_packet = pong_packet
        if int(self.pong_packet) == self.ping_packet:
            self.fail = False
        return self.fail


# Add ESP device
esp_b01 = EspDevice('big', '01')

# MQTT client
mqttc = mqtt.Client()
mqttc.username_pw_set(config.CONFIG['MQTT_USER'], config.CONFIG['MQTT_PASSWORD'])

try:
    mqttc.connect(config.CONFIG['MQTT_BROKER'], config.CONFIG['MQTT_PORT'])
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
except Exception as error:
    print("Error in MQTT connection: [Exception] %s: %s" % (type(error).__name__, error))


async def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        command = msg['text']
        if command == '/start':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Инфо'), dict(text='Маленькая ванная'), dict(text='Большая ванная')]
            ], resize_keyboard=True)
            await bot.sendMessage(chat_id, 'Привет! Я бот слежения за утечками. Выбери раздел', reply_markup=markup)

        elif command == 'Главное меню':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Инфо'), dict(text='Маленькая ванная'), dict(text='Большая ванная')]
            ], resize_keyboard=True)
            await bot.sendMessage(chat_id, 'Выбери раздел', reply_markup=markup)

        elif command == u'Инфо':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Главное меню')],
            ], resize_keyboard=True)
            await bot.sendMessage(chat_id, 'Выбери объект', reply_markup=markup)

        elif command == u'Маленькая ванная':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Закрыть краны (м)'), dict(text='Открыть краны (м)')],
                [dict(text='Закрыть горячую (м)'), dict(text='Закрыть холодную (м)')],
                [dict(text='Открыть горячую (м)'), dict(text='Открыть холодную (м)')],
                [dict(text='Главное меню')],
            ], resize_keyboard=True)
            await bot.sendMessage(chat_id, 'Управление маленькой ванной. Выбери задачу', reply_markup=markup)

        elif command == u'Закрыть краны (м)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'small/tap/cold', 'close')
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'small/tap/hot', 'close')
            await bot.sendMessage(chat_id, 'Краны закрыты')

        elif command == u'Открыть краны (м)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'small/tap/cold', 'open')
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'small/tap/hot', 'open')
            await bot.sendMessage(chat_id, 'Краны открыты')

        elif command == u'Закрыть горячую (м)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'small/tap/hot', 'close')
            await bot.sendMessage(chat_id, 'Кран горячей воды закрыт')

        elif command == u'Закрыть холодную (м)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'small/tap/cold', 'close')
            await bot.sendMessage(chat_id, 'Кран холодной воды закрыт')

        elif command == u'Открыть горячую (м)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'small/tap/hot', 'open')
            await bot.sendMessage(chat_id, 'Кран горячей воды открыт')
            await bot.sendMessage(chat_id, 'Кран холодной воды открыт')

        elif command == u'Открыть холодную (м)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'small/tap/cold', 'open')

        elif command == u'Большая ванная':
            markup = ReplyKeyboardMarkup(keyboard=[
                [dict(text='Закрыть краны (б)'), dict(text='Открыть краны (б)')],
                [dict(text='Закрыть горячую (б)'), dict(text='Закрыть холодную (б)')],
                [dict(text='Открыть горячую (б)'), dict(text='Открыть холодную (б)')],
                [dict(text='Главное меню')],
            ], resize_keyboard=True)
            await bot.sendMessage(chat_id, 'Управление большой ванной. Выбери задачу', reply_markup=markup)

        elif command == u'Закрыть краны (б)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'big/tap/cold', 'close')
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'big/tap/hot', 'close')
            await bot.sendMessage(chat_id, 'Краны закрыты')

        elif command == u'Открыть краны (б)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'big/tap/cold', 'open')
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'big/tap/hot', 'open')
            await bot.sendMessage(chat_id, 'Краны открыты')

        elif command == u'Закрыть горячую (б)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'big/tap/hot', 'close')
            await bot.sendMessage(chat_id, 'Кран горячей воды закрыт')

        elif command == u'Закрыть холодную (б)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'big/tap/cold', 'close')
            await bot.sendMessage(chat_id, 'Кран холодной воды закрыт')

        elif command == u'Открыть горячую (б)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'big/tap/hot', 'open')
            await bot.sendMessage(chat_id, 'Кран горячей воды открыт')

        elif command == u'Открыть холодную (б)':
            mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + 'big/tap/cold', 'open')
            await bot.sendMessage(chat_id, 'Кран холодной воды открыт')
    print(msg)


async def check_esp():
    global ping_iterator, ping_device_error
    while True:
        esp_b01.ping(ping_iterator)
        await asyncio.sleep(10)
        if esp_b01.fail is not False:
            if ping_device_error > config.CONFIG['MQTT_DEVICE_MAX_ERROR']:
                await bot.sendMessage(config.CONFIG['TELEGRAM_GROUP_CHAT_ID'], "Отказ в большой ванне устройства № 1")
                print("Отказ в большой ванне устройства № 1")
                ping_device_error = 0
            ping_device_error += 1
        ping_iterator += 1


async def check_mqtt():
    global ping_fail, ping_mqtt
    while True:
        await asyncio.sleep(10)
        ping_mqtt = time.time()
        mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + "state/check/mqtt", "%s" % str(ping_mqtt))
        print("Send MQTT ping (%s)" % ping_mqtt)
        ping_fail += 1
    
        if ping_fail >= 5:
            print("MQTT ping false... reconnect (%i)" % ping_fail)
            try:
                mqttc.reconnect()
                mqttc.publish(config.CONFIG['MQTT_BOT_TOPIC'] + "state", 'Reconnect to server')
                await bot.sendMessage(config.CONFIG['TELEGRAM_GROUP_CHAT_ID'], "Переподключение к серверу MQTT")
                ping_fail = 0
            except Exception as error:
                print("Error in MQTT reconnection: [Exception] %s: %s" % (type(error).__name__, error))


mqttc.loop_start()

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot, {'chat': on_chat_message}).run_forever())
loop.create_task(check_esp())
loop.create_task(check_mqtt())

print('Listening ...')

loop.run_forever()
