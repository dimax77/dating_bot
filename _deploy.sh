#!/bin/bash

set -e

# Настройки
SERVER="mockingb@95.164.62.113"
DIR="/home/mockingb/dating_bot"
DOMAIN="dating.viewdns.net"
EMAIL="y335ex@gmail.com"  # email для Let's Encrypt
SUDO_PASSWORD="Innopolis2023"

# 1. Подключение и деплой
ssh -t $SERVER << EOF
  set -e

  echo "🔄 Проверяем наличие репозитория на сервере..."
  if [ ! -d "$DIR" ]; then
    git clone git@github.com:dimax77/dating_bot.git $DIR
  else
    cd $DIR && git pull
  fi

  cd $DIR

  echo "🐳 Обновляем Docker Compose (правка пути к Dockerfile, если нужно)..."
  sed -i 's|build: ./app|build:\n      context: .\n      dockerfile: Dockerfile|' docker-compose.yml

  echo "💡 [1/4] Поднимаем сервисы..."
  docker compose up -d web nginx

  echo "📦 Проверка и установка certbot, если нужно..."
  if ! command -v certbot &> /dev/null; then
    echo "$SUDO_PASSWORD" | sudo -S apt update
    echo "$SUDO_PASSWORD" | sudo -S apt install -y certbot python3-certbot-nginx
  else
    echo "✅ Certbot уже установлен"
  fi

  echo "🔐 [2/4] Получаем сертификат от Let's Encrypt, если ещё нет..."
  if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "$SUDO_PASSWORD" | sudo -S certbot certonly --nginx --agree-tos --no-eff-email --email $EMAIL -d $DOMAIN
  else
    echo "📄 Сертификат уже существует, пропускаем"
  fi

  echo "🔁 [3/4] Перезапускаем nginx с HTTPS..."
  if systemctl list-units --type=service --all | grep -q nginx.service; then
    echo "$SUDO_PASSWORD" | sudo -S systemctl reload nginx
  else
    echo "⚠️ Сервис nginx не найден — проверь docker/nginx setup"
  fi

  echo "♻️ [4/4] Настраиваем автообновление сертификатов..."
  if systemctl list-unit-files | grep -q certbot.timer; then
    echo "$SUDO_PASSWORD" | sudo -S systemctl enable certbot.timer
    echo "$SUDO_PASSWORD" | sudo -S systemctl start certbot.timer
  else
    echo "⚠️ certbot.timer не найден — возможно certbot установлен в Docker?"
  fi

  echo "✅ Готово! Приложение доступно по адресу: https://$DOMAIN"
EOF
