FROM ubuntu
MAINTAINER Bulanov Konstantin <leech001@gmail.com>

ADD config /opt/config
WORKDIR /opt/

RUN apt-get update
RUN apt-get install -y mosquitto

CMD [ "mosquitto" ]
