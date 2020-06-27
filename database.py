from datetime import datetime
from pymongo import MongoClient
import re

from bson.objectid import ObjectId

from flask_admin.contrib.pymongo import ModelView, filters
from flask_security import UserMixin, RoleMixin

from mongoengine import connect, Document, IntField, \
                        StringField, BooleanField, ReferenceField, \
                        ListField, DateTimeField, ObjectIdField, \
                        EmbeddedDocument, EmbeddedDocumentListField


from posts.forms import PostForm

from config import Config

connect(
    db='testposts',
    host=Config.DB_URI
)

# client = MongoClient(Config.DB_URI)
# db = client.testposts # TODO change to blogDB later
# posts = db.posts

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

    # def __repr__(self):
    #     return f'Tag name: {self.name}'

    # def obj(self):
    #     return {
    #         'name': self.name,
    #         'slug': self.slug
    #     }

# TODO user and userinfo
class Post(Document):

    # _id = ObjectIdField(required=True, unique=True, primary_key=True)
    date = DateTimeField(default=datetime.now())
    title = StringField(max_length=140)
    slug = StringField(max_length=140, unique=True)
    body = StringField()
    tags = EmbeddedDocumentListField(Tag, default=[])
    meta = {'collection': 'posts'}

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
        
        
        
        
        # self.tags = []

        # if post: 
        #     self.title = post['title']
        #     self.body = post['body']
            
        #     if not post['slug']:
        #         self.slug = slugify(post['title'])

           
    # def obj(self):
    #     return {
    #         'date': self.date,
    #         'slug': self.slug,
    #         'title': self.title,
    #         'body': self.body
    #     }


    # def __repr__(self):
    #     return f'Post title: {self.title}'

 



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

        # Grab user names
        query = {'_id': {'$in': [x['_id'] for x in data]}}
        # users = db.user.find(query, {'name': 1})

        # Contribute user names to the models
        users_map = dict((x['_id'], x['name']) for x in users)

        for item in data:
            item['user_name'] = users_map.get(item['_id'])

        return count, data

    def on_model_change(self, form, model, is_created):
        user_id = model.get('user_id')
        model['user_id'] = ObjectId(user_id)

        model['slug'] = slugify(model['title'])
        model['date'] = datetime.now()

        return super(PostView, self).on_model_change(form, model, is_created)


### Flask Security

class Role(Document, RoleMixin): 

    # id = IntField(primary_key=True)
    name = StringField(max_length=100, unique=True)
    description = StringField(max_length=255)

class User(Document, UserMixin): 

    # id = IntField(primary_key=True)
    email = StringField(max_length=255, unique=True)
    password = StringField(max_length=255)
    active = BooleanField()
    roles = ListField(ReferenceField(Role), default=[])
    meta = {'strict': False}



