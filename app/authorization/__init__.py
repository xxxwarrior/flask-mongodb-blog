from flask import Blueprint

auth_bp = Blueprint('authorization', __name__, template_folder='templates')

from app.authorization import routes