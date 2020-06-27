from datetime import datetime
from pymongo import MongoClient
import re

from config import Config

client = MongoClient(Config.DB_URI)
db = client.testposts # change to blogDB later

def slugify(s):
    pattern = r'[\W+]'
    return re.sub(pattern, '-', s).lower()


class Post: 
    def __init__(self, title, body, user):
        self.date = datetime.now()
        self.slug = slugify(title)
        self.title = title
        self.body = body
        self.username = user.name

    def __repr__(self):
        return f'Post title: {self.title}'

    
    # not sure at all
    def postObject(self):
        return {
            'date': self.date,
            'slug': self.slug,
            'title': self.title,
            'body': self.body,
            'username': self.username
        }




    


