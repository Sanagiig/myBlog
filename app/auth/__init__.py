from flask import blueprints
auth = blueprints.Blueprint('auth',__name__)
from app.auth import views