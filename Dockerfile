FROM python:3.6-alpine
MAINTAINER Marc Visa Pascual
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY app ./app
COPY TFG ./TFG
COPY templates ./templates
COPY manage.py ./

ADD requirements.txt /app/
ADD . /app/

ENV PORT 8000
EXPOSE $PORT
RUN python manage.py migrate
CMD gunicorn -b 0.0.0.0:$PORT TFG.wsgi
RUN adduser -D user
USER user
