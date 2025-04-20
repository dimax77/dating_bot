# app/__init__.py
from flask import Flask
from app.routes import main
from app.db.init_db import init_db
import os

import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_app():

    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(base_dir, 'static')
    templates_dir = os.path.join(base_dir, 'templates')

    app = Flask(__name__, static_folder=static_dir, template_folder=templates_dir)

    app.secret_key = 'supersecretkey'
    app.register_blueprint(main)

    # Вызов init_db после создания app
    with app.app_context():
        init_db()

    return app

