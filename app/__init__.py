from flask import Flask
from app.routes import main
from app.routes import init_db


def create_app():
    init_db()

    app = Flask(__name__)
    app.secret_key = 'supersecretkey'
    app.register_blueprint(main)
    return app

