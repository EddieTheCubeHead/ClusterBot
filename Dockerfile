FROM python:3.11-alpine3.17

ARG BOT_TOKEN

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "bot.py"]