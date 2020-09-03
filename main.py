from app import app
from posts.blueprint import posts
from authorization.blueprint import authorization
import view

app.register_blueprint(authorization)
app.register_blueprint(posts, url_prefix='/blog')


if __name__ == '__main__':
    app.run()