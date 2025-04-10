set -e


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

  cd flask-test
  docker compose up --build



  echo "✅ Готово! Приложение доступно по адресу: https://$DOMAIN"
EOF
