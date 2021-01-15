""" This script is used to seed the database with initial data: 
a demo post, admin role and admin user """



from pymongo import MongoClient
from mongoengine import connect, disconnect
from os import environ
from dotenv import load_dotenv, find_dotenv

from app.database import User, Post


load_dotenv(find_dotenv())
host = environ.get('DB_URI')
print('yep')

disconnect(alias='default')
connect(
    db='myDatabase',
    alias='default',
    host=host
)
print('hm')

if not Post.objects(title="demopost"):
    print('hey')
    Post(title="demopost", body="demobody").save()


if not User.objects(name="admin"): 
    print('yey')
    client = MongoClient(host)
    db = client.myDatabase

    db.role.update_one({"name": "admin"}, {"$set": {"name": "admin", "description": "Admin Role gives privileges of deleting and editing all the posts as well as commentaries and opens admin menu"}}, upsert=True)
    admin_role = db.role.find_one({"name": "admin"})['_id']

    usr = User.objects(name="admin").modify(upsert=True, new=True, set__email="admin", set__roles=[admin_role])
    usr.set_password("1234")
    usr.save()

print('ts')






