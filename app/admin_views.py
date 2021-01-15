from datetime import datetime

from flask import redirect, url_for, request
from flask_security import current_user
from flask_admin import AdminIndexView
from flask_admin.contrib.mongoengine import ModelView, filters

from .database import Post, slugify
from app.posts.forms import PostForm


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

# The users are not shown in admin view, might add them
    # def get_list(self, *args, **kwargs):
    #     count, data = super(PostView, self).get_list(*args, **kwargs)
    #     # users = User.objects(_id__in=[x['_id'] for x in data]).fields(_id=1, name=1)
    #     # users_map = dict((x['_id'], x['name']) for x in users)
    #     # for item in data:
    #     #     item['user_name'] = users_map.get(item['_id']
    #     return count, data

    def on_model_change(self, form, model, is_created):
        # user_id = model.user.id
        # model['user_id'] = ObjectId(user_id)

        model['slug'] = slugify(model['title'])
        model['date'] = datetime.now()

        return super(PostView, self).on_model_change(form, model, is_created)




class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('authorization.login', next=request.url))

class AdminView(AdminMixin, PostView):
    pass

class HomeAdminView(AdminMixin, AdminIndexView):
    pass


