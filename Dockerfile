FROM python:3.6-alpine
MAINTAINER Marc Visa Pascual

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

ADD requirements.txt /app/
ADD . /app/

RUN adduser -D user
USER user
