import re
from datetime import datetime

from bson.objectid import ObjectId
from flask_security import UserMixin, RoleMixin
from mongoengine import Document, connect, StringField, BooleanField,\
                        ReferenceField, ListField, DateTimeField, \
                        LazyReferenceField, FileField, ObjectIdField, \
                        EmbeddedDocument, EmbeddedDocumentListField    
from werkzeug.security import generate_password_hash, check_password_hash         

from config import Config


def get_db(app):
    client = app.config['SESSION_MONGODB']
    db = client[app.config['DB']]
    return db


##--// User Management \\--##
class Role(Document, RoleMixin): 

    name = StringField(max_length=100, unique=True)
    description = StringField(max_length=255)

class User(Document, UserMixin): 

    name = StringField(max_length=100)
    email = StringField(max_length=255, unique=True)
    password = StringField(max_length=255)
    active = BooleanField()
    roles = ListField(ReferenceField(Role), default=[])
    meta = {'strict': False}
    # would be cool to store user's posts also

    def is_active(self):
        return True

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



##--// Posts Management \\--##
# TODO make better handling of slugs' duplicates

def slugify(s):
    pattern = r'[\W+]'
    return re.sub(pattern, '-', s).lower()

class Comment(EmbeddedDocument):

    oid = ObjectIdField(default=ObjectId(), required=True, primary_key=True)
    date = DateTimeField(default=datetime.now().isoformat(sep=' ', timespec='minutes'))
    author = ReferenceField(User, required=True)
    body = StringField(max_length=1000)


class Tag(EmbeddedDocument):

    name = StringField(max_length=140, required=True)
    slug = StringField(max_length=140)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)


class Post(Document):

    date = DateTimeField(default=datetime.now().isoformat(sep=' ', timespec='minutes'))
    title = StringField(max_length=140, required=True, min_length=1, null=False)
    slug = StringField(max_length=140, unique=True)
    body = StringField()
    tags = EmbeddedDocumentListField(Tag, default=[])
    user = LazyReferenceField(User, default=None, reverse_delete_rule=1)
    picture = FileField()
    pic_name = StringField()
    comments = EmbeddedDocumentListField(Comment, default=[])


    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        self.slug = slugify(self.title)