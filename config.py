from pymongo import MongoClient

class Config(object):
    DEBUG = True
    DB_URI = "mongodb+srv://Admin:Admin1@cluster0-6fxtf.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
    SESSION_TYPE = 'mongodb'
    SESSION_MONGODB = MongoClient(DB_URI)
    SECRET_KEY = "Super secret key"
    MONGODB_HOST = DB_URI
    MONGODB_DB = True
    UPLOAD_FOLDER = r"D:\Development\projects\blog\app\static\upload"

    # Flask Security
    SECURITY_PASSWORD_SALT = 'salt'
    SECURITY_PASSWORD_HASH = 'bcrypt'
 
    
