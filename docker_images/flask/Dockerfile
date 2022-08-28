FROM python:3.6

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/flaskapp/src
COPY requirements.txt /opt/services/flaskapp/src/
WORKDIR /opt/services/flaskapp/src
RUN pip install six
RUN pip install requests
RUN pip install -r requirements.txt
COPY . /opt/services/flaskapp/src
EXPOSE 5090
RUN pip install gunicorn[gevent]
RUN python src/wsgi.py
#RUN gunicorn src.wsgi:app -b localhost:5090 --worker-class gevent &