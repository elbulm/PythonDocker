from flask import Flask, request, url_for, render_template
from .application import main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_blueprint)
    return app