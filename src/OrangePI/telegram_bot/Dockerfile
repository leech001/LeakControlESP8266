FROM python:3
MAINTAINER Bulanov Konstantin <leech001@gmail.com>

ADD app /opt/app
WORKDIR /opt/app

RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "./telegrambot.py" ]
