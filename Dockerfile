FROM python:3.11-alpine3.17

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]