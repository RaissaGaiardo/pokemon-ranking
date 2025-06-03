FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y cron gcc g++ libpq-dev && \
    pip install --upgrade pip

WORKDIR /app

# Copia apenas os arquivos relevantes
COPY main.py /app/
COPY requirements.txt /app/
COPY entrypoint.sh /entrypoint.sh
COPY credentials /app/credentials

RUN pip install -r /app/requirements.txt

RUN chmod +x /entrypoint.sh

# Cronjob para rodar todo dia à meia-noite
RUN echo "0 0 * * * /usr/local/bin/python /app/main.py >> /app/cron.log 2>&1" > /etc/cron.d/pokemon-cron
RUN chmod 0644 /etc/cron.d/pokemon-cron && crontab /etc/cron.d/pokemon-cron

ENTRYPOINT ["/entrypoint.sh"]
