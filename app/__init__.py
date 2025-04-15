from flask import Flask
from app.routes import main
from app.routes import init_db
import os


def create_app():
    init_db()

    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'),)
    app.secret_key = 'supersecretkey'
    app.register_blueprint(main)
    return app

