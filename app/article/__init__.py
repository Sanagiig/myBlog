from flask import blueprints
art = blueprints.Blueprint('art',__name__)
from app.article import views