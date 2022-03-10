import os
from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_cors import CORS
# from flask_googlemaps import GoogleMaps
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
app._static_folder = os.path.abspath("static/")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"
bootstrap = Bootstrap(app)

app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET')  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)

# ading a comment, hope this works
# Initialize the extension
# GoogleMaps(app)

# ...
def create_app(config_class=Config):
    app = Flask(__name__)
    # ...

    #app.api was not working while in here

# ...

from app import routes, models, errors

