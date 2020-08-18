from flask import Flask, redirect, url_for, request
from pymongo import MongoClient
from config import Config

from jinja2 import ChoiceLoader, FileSystemLoader
from flask_admin import Admin, AdminIndexView

from flask_session import Session 
from flask_security import Security, MongoEngineUserDatastore, current_user
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_login import LoginManager

from flask_bcrypt import Bcrypt

from database import Post, User, Role
from model_views import PostView

app = Flask(__name__) 
app.config.from_object(Config)
app.static_folder = app.root_path + r"\static"
app.secret_key = Config.SECRET_KEY

session = Session()
session.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'authorization.login'


bcrypt = Bcrypt(app)

client = Config.SESSION_MONGODB
db = MongoEngine(app)
users = client.test.user
# app.session_interface = MongoEngineSessionInterface(db)


class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('authorization.login', next=request.url))

class AdminView(AdminMixin, PostView):
    pass

class HomeAdminView(AdminMixin, AdminIndexView):
    pass



admin = Admin(app, 'FlaskApp', url='/', index_view=HomeAdminView(name='home'))
admin.add_view(AdminView(Post, name='Posts'))

user_datastore = MongoEngineUserDatastore(users, User, Role)
# security = Security(app, user_datastore, register_blueprint=False)


