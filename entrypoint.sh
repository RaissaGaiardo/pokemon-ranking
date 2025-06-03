#!/bin/bash
# Inicia o cron em background
service cron start

# Mantém o container rodando mostrando o log do cron
tail -f /app/cron.log
