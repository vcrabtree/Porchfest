import os
from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_cors import CORS

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "support@porchfest.live"
app.config['MAIL_PASSWORD'] = "iTown1892*"

mail = Mail(app)
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
if os.environ.get("DEV_MODE") == "dev":
    app.config["EMAIL_SERVER"] = "http://localhost:5000/password_reset/"
    app.config["ENVIRONMENT"] = "http://localhost:3000/"
else:
    app.config["EMAIL_SERVER"] = "https://api.porchfest.live/password_reset/"
    app.config["ENVIRONMENT"] = "https://porchfest.live/"
jwt = JWTManager(app)


def create_app(config_class=Config):
    app = Flask(__name__)


from app import routes, artist_routes, user_routes, log_reg_routes, models, errors
