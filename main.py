from app import create_app

from flask import render_template
from flask_admin import Admin

from app.database import Post 
from app.admin_views import AdminView, HomeAdminView


app = create_app()
print(app.config['DB'])

admin = Admin(app, 'FlaskApp', url='/', index_view=HomeAdminView(name='home'))
admin.add_view(AdminView(Post, name='Posts'))

if __name__ == '__main__':
    app.run()