from flask import Blueprint

posts_bp = Blueprint('posts_bp', __name__, template_folder='templates')

from app.posts import routes