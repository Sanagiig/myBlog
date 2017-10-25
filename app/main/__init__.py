from flask import blueprints
main = blueprints.Blueprint('main',__name__)
from app.main import views