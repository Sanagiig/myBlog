from flask import blueprints
user = blueprints.Blueprint('user',__name__)
from app.user import views