FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install flask gunicorn

CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app:create_app()"]
