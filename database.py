from datetime import datetime
from pymongo import MongoClient
import re

from bson.objectid import ObjectId

from flask_security import UserMixin, RoleMixin
from mongoengine import connect, Document, IntField, \
                        StringField, BooleanField, ReferenceField, \
                        ListField, DateTimeField, LazyReferenceField, \
                        EmbeddedDocument, EmbeddedDocumentListField, \
                        FileField
                        

from config import Config

connect(
    db='testposts',
    alias='posts-db',
    host=Config.DB_URI
)

connect(
    db='test',
    alias='default',
    host=Config.DB_URI
)

# client = MongoClient(Config.DB_URI)
# db = client.testposts # TODO change to blogDB later
# posts = db.posts


### Flask Security ###

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


### Posts Management ###

# TODO make better handling of slugs, their duplicate and after edition behavior

def slugify(s):
    pattern = r'[\W+]'
    return re.sub(pattern, '-', s).lower()


class Tag(EmbeddedDocument):

    name = StringField(max_length=140)
    slug = StringField(max_length=140)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        if self.name:
            self.slug = slugify(self.name)


class Post(Document):

    date = DateTimeField(default=datetime.now())
    title = StringField(max_length=140)
    slug = StringField(max_length=140, unique=True)
    body = StringField()
    tags = EmbeddedDocumentListField(Tag, default=[])
    user = LazyReferenceField(User, default=None, reverse_delete_rule=1)
    picture = FileField()
    pic_name = StringField()
    meta = {'collection': 'posts',
            'db_alias': 'posts-db'}

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
