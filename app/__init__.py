from flask import Flask
from app.routes import main

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'
    app.register_blueprint(main)
    return app
