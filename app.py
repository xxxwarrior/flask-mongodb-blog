from flask import Flask, redirect, url_for, request
from pymongo import MongoClient
from config import Config

from flask_admin import Admin, AdminIndexView
from flask_session import Session 
from flask_security import Security, MongoEngineUserDatastore, current_user
from flask_mongoengine import MongoEngine 

from database import PostView, Post, User, Role

app = Flask(__name__, static_folder=r"C:\Development\projects\blog\app\static\css") 
app.config.from_object(Config)
Session(app)
app.secret_key = Config.SECRET_KEY


client = Config.SESSION_MONGODB
# db = client.testposts
db = MongoEngine(app)
users = client.testusers.users


class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))

class AdminView(AdminMixin, PostView):
    pass

class HomeAdminView(AdminMixin, AdminIndexView):
    pass



admin = Admin(app, 'FlaskApp', url='/', index_view=HomeAdminView(name='home'))
admin.add_view(AdminView(Post, name='Posts'))

user_datastore = MongoEngineUserDatastore(users, User, Role)
security = Security(app, user_datastore)


