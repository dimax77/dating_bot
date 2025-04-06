#!/bin/bash

set -e

# Настройки сервера и домена
SERVER="mockingb@95.164.62.113"
DIR="/home/mockingb/dating_bot"
SERVICE="dating_bot"
DOMAIN="dating.viewdns.net"
EMAIL="you@example.com"  # или пусто --register-unsafely-without-email
WEBROOT_PATH="./certbot/www"

# 1. Подключение к серверу и деплой
ssh $SERVER << EOF
  echo "🔄 Проверяем наличие репозитория на сервере..."
  
  # Если директория проекта не существует, клонируем репозиторий
  if [ ! -d "$DIR" ]; then
    git clone git@github.com:dimax77/dating_bot.git $DIR
  else
    cd $DIR && git pull
  fi

  cd $DIR

  # 2. Проверка и запуск службы
  if [ ! -f "/etc/systemd/system/$SERVICE.service" ]; then
    echo "🔧 Устанавливаем службу $SERVICE..."
    sudo cp service/$SERVICE.service /etc/systemd/system/
    sudo systemctl daemon-reexec
    sudo systemctl enable $SERVICE
    sudo systemctl start $SERVICE
  else
    echo "📦 Служба $SERVICE уже существует, пропускаем создание"
  fi

  # 3. Проверка и обновление cron-задачи
  crontab -l | grep -q "$DIR/deploy.sh" || (crontab -l; echo "0 * * * * $DIR/deploy.sh") | crontab -
EOF

# 4. Настройка сертификата с Let's Encrypt и запуск Docker
echo "💡 [1/4] Поднимаем сервисы..."
docker compose up -d web nginx

# Проверка существования сертификата и его обновление
if [ ! -f "./certbot/conf/live/$DOMAIN/fullchain.pem" ]; then
  echo "🔐 [2/4] Получаем сертификат от Let's Encrypt..."
  docker run --rm \
    -v "$PWD/certbot/www:/var/www/certbot" \
    -v "$PWD/certbot/conf:/etc/letsencrypt" \
    certbot/certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --agree-tos --no-eff-email \
    --email $EMAIL \
    -d $DOMAIN
else
  echo "📄 Сертификат уже существует, пропускаем получение"
fi

# 5. Перезапуск Nginx с новым сертификатом
echo "🔁 [3/4] Перезапускаем nginx с HTTPS..."
docker compose restart nginx

# 6. Запуск автообновления certbot
echo "♻️ [4/4] Поднимаем автообновление certbot..."
docker compose up -d certbot

echo "✅ Готово! Приложение доступно по адресу: https://$DOMAIN"
