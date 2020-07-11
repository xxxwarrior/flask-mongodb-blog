from wtforms import Form, Field, StringField, TextAreaField
from wtforms.widgets import TextInput

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
