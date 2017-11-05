# Система контроля утечек воды (Leak Control) на базе ESP8266 (NodeMCU)

Простейшая система по контролю утечек (протечек) в местах водаразбора.

## Создается на основе следующих компонентов:
1. NodeMCU https://ru.aliexpress.com/item/New-Wireless-module-NodeMcu-Lua-WIFI-Internet-of-Things-development-board-based-ESP8266-with-pcb-Antenna/32453920794.html?spm=a2g0s.8937460.0.0.JigHr0
2. MotorShield https://ru.aliexpress.com/item/Free-shipping-NodeMCU-Motor-Shield-Board-L293D-for-ESP-12E-from-ESP8266-esp-12E-kit-diy/32390158973.html?spm=a2g0s.9042311.0.0.D74QiD
3. OrangePI https://ru.aliexpress.com/item/Orange-Pi-PC-Plus-SET5-Orange-Pi-PC-Plus-Transparent-ABS-Case-Power-Supply-Development-Board/32669760149.html?aff_platform=aaf&cpt=1509804021129&sk=zj6qB6AIM&aff_trace_key=f3963e4de0624f27815fadab5c75d4c9-1509804021129-04173-zj6qB6AIM&terminal_id=d22fe22f4cee4ee2b8c1ffaa2f6a46d4
4. Блок питания для кранов https://ru.aliexpress.com/item/12V2A-AC-100V-240V-Power-Adapter-Converter-Power-Supply-3528-5050-LED-strip-power-EU-UK/32739387151.html?spm=a2g0s.9042311.0.0.D74QiD
5. Преобразователь напряжения https://ru.aliexpress.com/item/5pcs-lot-Max-DC-DC-XL4005-Step-5A-Down-Adjustable-Power-Supply-Module-LED-Lithium-Charger/32750014775.html?spm=a2g0s.9042311.0.0.rMOtsC
6. Шаровый кран https://ru.aliexpress.com/item/Free-Shipping-Motorized-ball-valve-DN15-2-way-electrical-valve/1000001800120.html?spm=a2g0s.9042311.0.0.Gt07FS
7. Датчик утечки https://ru.aliexpress.com/item/Smart-Electronics-For-Arduino-Diy-Starter-Kit-3-3-5V-Raindrops-Rain-Weather-Humidity-Sensitive-Detection/32460014764.html?algo_expid=3311d6e8-fdd3-4d1f-a9b3-d314977e3a34-0&algo_pvid=3311d6e8-fdd3-4d1f-a9b3-d314977e3a34&btsid=bd5f14a8-674e-4704-a814-69060c25c5b8&spm=a2g0v.search0104.3.2.Np7ZTv&ws_ab_test=searchweb0_0%252Csearchweb201602_0_10152_10065_10151_10068_10344_10345_10342_10343_10340_10341_10543_10541_10307_10301_10060_10155_10154_10056_10055_10539_10537_10536_10059_10534_10533_100031_10103_10102_10169_10142_10107_10084_10083_10312_10313_10314_10211_10550_10073_10551_10128_10552_10129_10553_10554_10555_10557_10125-10552%252Csearchweb201603_0%252CppcSwitch_0&aff_platform=link-c-tool&cpt=1509881813630&sk=uR7uBY3Rz&aff_trace_key=32ea7e16b8414ba68a0f8f9aa43263fe-1509881813630-01733-uR7uBY3Rz&terminal_id=d22fe22f4cee4ee2b8c1ffaa2f6a46d4

## Принцип работы
1. На OrangePI или аналоги устаннавливается MQTT Broker (mosquito) который слушает события.
2. Запускается Python скрипт для уведомлений и управления посредством Telegram бота (Telepot).
3. Заливается прошивка MicroPython http://micropython.org/download#esp8266
4. На плату NodeMCU записываются скрипты из папки ESP8266


Датчики утечки раскладываются в местах возможных утечек. В случае намокания элемента и поступления сигнала на ножку ESP8266 отрабатывает скрипт и на краны автоматически поступает сигнал на закрытие.
Так же формируется событие через MQTT, что произошла утечка и через скрипт wbot.py данное уведомление направляется в соответствующую группу в Telegram через Telegram Bot.
Управление кранами также доступно через специальную клавиатуру управления Telegram Bot.


 