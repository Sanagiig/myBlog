from flask import Flask,current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from threading import Thread
from config import config


app = Flask(__name__)
db = SQLAlchemy()
mail = Mail()
moment = Moment()
login_manager = LoginManager()

def create_app(config_name='default'):
    config_name = 'default'
    app.config.from_object(config[config_name])
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    from app.article import art as art_blueprint
    app.register_blueprint(art_blueprint,url_prefix='/article')

    from app.user import user as user_blueprint
    app.register_blueprint(user_blueprint,url_prefix='/user')

    db.app=app
    db.create_all()

    # from app.public import generator
    # generator.generate_fake()
    return app





