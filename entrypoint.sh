#!/bin/bash

# Cria o arquivo de log se não existir
touch /app/cron.log

# Inicia o serviço cron em background
service cron start

# Exibe o log para acompanhar em tempo real
tail -f /app/cron.log

#!/bin/bash
python /app/main.py
tail -f /dev/null  # Mantém o container "vivo"
