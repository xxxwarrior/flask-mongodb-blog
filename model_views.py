from datetime import datetime

from flask_admin.contrib.mongoengine import ModelView, filters

from database import Post, slugify
from posts.forms import PostForm


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
        print(f'>>> count: {count}')
        print(f'>>> data: {data}')

        # users = User.objects(_id__in=[x['_id'] for x in data]).fields(_id=1, name=1)
        # users_map = dict((x['_id'], x['name']) for x in users)

        # for item in data:
        #     item['user_name'] = users_map.get(item['_id'])

        return count, data

    def on_model_change(self, form, model, is_created):
        # user_id = model.user.id
        print(model)
        # model['user_id'] = ObjectId(user_id)

        model['slug'] = slugify(model['title'])
        model['date'] = datetime.now()

        return super(PostView, self).on_model_change(form, model, is_created)




