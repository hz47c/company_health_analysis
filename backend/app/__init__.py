# app/__init__.py

from flask import Flask
from .financial_controller import financial_bp
from .db import db
from flask_cors import CORS
import sys

def create_app():
    app = Flask(__name__)
    
    print(f"Python version: {sys.version}")

    # Enable CORS for all routes and origins
     
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lh7.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(financial_bp)

    with app.app_context():
        db.create_all()  # Create tables if they don't exist

    return app
