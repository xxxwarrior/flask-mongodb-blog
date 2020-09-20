from flask_admin import Admin

from app import create_app
from app.database import Post 
from app.admin_views import AdminView, HomeAdminView

# TODO pass config via terminal
app = create_app()

admin = Admin(app, 'FlaskApp', url='/', index_view=HomeAdminView(name='home'))
admin.add_view(AdminView(Post, name='Posts'))

if __name__ == '__main__':
    app.run()