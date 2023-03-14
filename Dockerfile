FROM python:3.11-alpine3.17

VOLUME /app/persistence
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "clusterbot.py"]