FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt


CMD ["gunicorn", "--workers=4", "--timeout=60", "--bind=0.0.0.0:5000", "--access-logfile=-", "--error-logfile=-", "app.wsgi:app"]
