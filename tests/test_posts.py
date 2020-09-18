from bson.objectid import ObjectId
from app.database import get_db, User


def test_create_edit_post(client, app):

    # Login admin user since create and edit are available to admin only
    rv = client.post('/login', data=dict(
        email='Test@email',
        password='1234'
    ), follow_redirects=True)
    assert b"You logged in succesfully" in rv.data

    # Delete test posts if they exist
    db = get_db(app)
    db.post.delete_one({'title': 'TestTitle'})
    db.post.delete_one({'title': 'TestTitleEdit'})

    # Create test post
    rv = client.post('/blog/create', data=dict(
        title = 'TestTitle',
        body = 'TestBody'
    ), follow_redirects=True)
    assert b"Your post has been successfully created" in rv.data

    # Make sure the post is available 
    rv = client.get('/blog/testtitle', follow_redirects=True)
    assert rv.status_code == 200

    # Edit post 
    rv = client.post('/blog/edit/testtitle', data=dict(
        title='TestTitleEdit',
        body='TestBodyEdit',
        tags='Test,Tag'
    ))
    assert rv.status_code == 302

    # Make sure the new edited post is available 
    rv = client.get('/blog/testtitleedit', follow_redirects=True)
    assert rv.status_code == 200

    
    
