git add .
git commit -m"Some design updates"
git push
ssh 95.164.62.113 <<EOF
    cd dating_bot || exit 1
    git pull || exit 1
    docker-compose up --build -d || exit 1
EOF

