from wtforms import Form, Field, StringField, TextAreaField
from wtforms.widgets import TextInput

from wtforms import widgets
from flask_admin.form import Select2TagsField

from database import Post, Tag

# from app import app, db
# from models import *

# class AdvancedTagWidget(widgets.Select):
#     """
#         `Select2 <https://github.com/select2/select2>`_ styled select widget.
#         You must include select2.js, form-x.x.x.js and select2 stylesheet for it to
#         work.
#     """
#     def __call__(self, field, **kwargs):
#         # For select2 v4:
#         kwargs.setdefault('data-tags', '1')
#         # For select2 v3.x and vanilla flask-admin form.js:
#         #  kwargs.setdefault('data-role', u'select2-tags')

#         allow_blank = getattr(field, 'allow_blank', False)
#         if allow_blank and not self.multiple:
#             kwargs['data-allow-blank'] = u'1'

#         return super(AdvancedTagWidget, self).__call__(field, **kwargs)


# class AdvancedTagField(Select2TagsField, Field):
#     """
#     Custom tag field. Supports tags that do not exist yet.
#     """

#     widget = widgets.Select(multiple=True)

#     def _value(self):
#         if self.data:
#             return [tag.name for tag in self.data]
#         else:
#             return u''


#     def pre_validate(self, form):
#         # Prevent "not a valid choice" error
#         pass

#     def process_formdata(self, valuelist):

#         if valuelist:
#             try:
#                 self.data = []
#                 for tagname in valuelist:
#                     post = Post.objects(tags__match={"name": tagname}).first()
#                     for tag in post.tags:
#                         if tag.name == tagname and not tag in self.data:
#                             self.data.append(tag)
#             except AttributeError:
#                 self.data.append(Tag(name=tagname))
#         else:
#             self.data = []

#     def iter_choices(self):

#         self.blank_text = ""

#         posts = Post.objects()
#         print(posts[1])
#         tags = []
#         for post in posts:
#             if post.tags:
#                 for tag in post.tags:
#                     if tag not in tags:
#                         tags.append(tag)

#         if self.object_data:
#             model_tags = [tag for tag in self.object_data]
#         else: model_tags = []
#         print(f'model tags: {model_tags}')
#         print(f'data: {self.data}')
#         print(f'object: {self.object_data}')

#         self.choices = [[tag, tag.name] for tag in tags]
#         print(f'choices: {self.choices}')

#         # Yield empty object in order to have an empty placeholder
#         yield (u'__None', self.blank_text, self.data is None)

#         for value, label in self.choices:
#             yield (value, label, value in model_tags)


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return [tag.name for tag in self.data]
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = ', '.join([value.name for value in valuelist])
        else:
            self.data = []


class PostForm(Form):
    title = StringField('Title')
    body = TextAreaField('Body')
    tags = TagListField('Tags')
