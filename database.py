from datetime import datetime
from pymongo import MongoClient
import re

from bson.objectid import ObjectId

from flask_security import UserMixin, RoleMixin
from flask_admin.contrib.mongoengine import ModelView, filters
from mongoengine import connect, Document, IntField, \
                        StringField, BooleanField, ReferenceField, \
                        ListField, DateTimeField, LazyReferenceField, \
                        EmbeddedDocument, EmbeddedDocumentListField
                        


from posts.forms import PostForm

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

    def __repr__(self):
        return f'"{self.name}" tag'


# TODO user and userinfo
class Post(Document):

    date = DateTimeField(default=datetime.now())
    title = StringField(max_length=140)
    slug = StringField(max_length=140, unique=True)
    body = StringField()
    tags = EmbeddedDocumentListField(Tag, default=[])
    user = LazyReferenceField(User, default=None, reverse_delete_rule=1)
    meta = {'collection': 'posts',
            'db_alias': 'posts-db'}

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)

 
class PostView(ModelView): 

    column_list = ('title', 'date', 'body', 'tags', 'slug')
    column_sortable_list = ('title', 'date', 'tags')

# TODO: case insensitive search 
    column_filters = (filters.FilterEqual('title', 'Title'),
                      filters.FilterNotEqual('title', 'Title'),
                      filters.FilterLike('title', 'Title'),
                      filters.FilterNotLike('title', 'Title'),
                      filters.FilterEqual('body', 'Body'),
                      filters.FilterNotEqual('body', 'Body'),
                      filters.FilterLike('body', 'Body'),
                      filters.FilterNotLike('body', 'Body'))

    column_searchable_list = ('title', 'body')

    form = PostForm

    def get_list(self, *args, **kwargs):
        
        count, data = super(PostView, self).get_list(*args, **kwargs)
        

        # users = User.objects(_id__in=[x['_id'] for x in data]).fields(_id=1, name=1)
        # users_map = dict((x['_id'], x['name']) for x in users)

        # for item in data:
        #     item['user_name'] = users_map.get(item['_id'])

        return count, data

    def on_model_change(self, form, model, is_created):
        user_id = model.get('user_id')
        model['user_id'] = ObjectId(user_id)

        model['slug'] = slugify(model['title'])
        model['date'] = datetime.now()

        return super(PostView, self).on_model_change(form, model, is_created)




