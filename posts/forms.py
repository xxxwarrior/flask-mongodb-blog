from wtforms import Form, Field, StringField, TextAreaField
from wtforms.widgets import TextInput
from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from database import Tag


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            tags = [tag.name for tag in self.data]
            return ', '.join(tags)
        else:
            return u''

    def process_formdata(self, valuelist):
        self.data = []
        if valuelist:
            valuelist = "".join(valuelist).split(", ")
            for value in valuelist:
                self.data.append(Tag(name=value)) 

class PostForm(Form):
    title = StringField('Title')
    body = TextAreaField('Body')
    tags = TagListField('Tags')
    picture = FileField('Picture')
