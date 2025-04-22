# app/__init__.py
from flask import Flask
from app.routes import main
from app.api.geo import geo
from app.db.init_db import init_db
import os, sys
import logging
from logging.handlers import RotatingFileHandler


def create_app():

    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(base_dir, 'static')
    templates_dir = os.path.join(base_dir, 'templates')

    app = Flask(__name__, static_folder=static_dir, template_folder=templates_dir)
    # app.secret_key = 'supersecretkey'
    app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key")



    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))
    file_handler.setLevel(logging.INFO)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.info("App startup")

    # Только если нужно логировать в консоль (например, в dev):
    if app.config.get("ENV") == "development":
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s"
        ))
        app.logger.addHandler(stream_handler)

    app.logger.info("App startup")


    # Регистрация блюпринтов и инициализация БД
    app.register_blueprint(main)
    app.register_blueprint(geo)


    # Вызов init_db после создания app
    with app.app_context():
        init_db()

    return app

