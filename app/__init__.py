# app/__init__.py
from flask import Flask
from app.routes import main
from app.routes import init_db
import os

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    init_db()

    # app = Flask(__name__, static_folder='static')
    # logger.info(f'Current dir been seen from __init__.py: {os.path.dirname(__file__)}')
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(base_dir, 'static')
    templates_dir = os.path.join(base_dir, 'templates')

    app = Flask(__name__, static_folder=static_dir, template_folder=templates_dir)


    # print(f'Current dir been seen from __init__.py: {os.path.dirname(__file__)}')
    app.secret_key = 'supersecretkey'
    app.register_blueprint(main)
    return app

