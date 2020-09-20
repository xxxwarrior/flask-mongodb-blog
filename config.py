from pymongo import MongoClient

from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Config(object):
    DEBUG = True
    TEMLATES_AUTO_RELOAD = True
 
    MONGODB_DB = True
    MONGODB_HOST = environ.get('DB_URI')

    SECRET_KEY = environ.get('SECRET_KEY')
    SESSION_TYPE = 'mongodb'
    SESSION_MONGODB = MongoClient(MONGODB_HOST)

    DB = 'deploy'
    
    STATIC_FOLDER = 'static'
    UPLOAD_FOLDER = environ.get('UPLOAD_FOLDER')

    # Flask Security
    SECURITY_PASSWORD_SALT = environ.get('SALT')
    SECURITY_PASSWORD_HASH = 'bcrypt'

class TestConfig(Config):
    TESTING = True
    DB = 'test'
    DEBUG = False
    WTF_CSRF_ENABLED = False

 
    
