from flask import Flask
from app.routes import main
from app.routes import init_db
import os

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    init_db()

    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    logger.info(f'Current dir been seen from __init__.py: {os.path.dirname(__file__)}')

    # print(f'Current dir been seen from __init__.py: {os.path.dirname(__file__)}')
    app.secret_key = 'supersecretkey'
    app.register_blueprint(main)
    return app

