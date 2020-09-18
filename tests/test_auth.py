from app.database import get_db

def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def registrate(client, name, email, password):
    return client.post('/register', data=dict(
        name=name, 
        email=email, 
        password=password
        ), follow_redirects=True)

def delete_user(db, usr):
    if db.user.find_one({'name': usr['name']}):
        db.user.delete_one({'name': usr['name']})

user = {
    'name': 'TestName',
    'email': 'Test@email',
    'password': '1234'
}


def test_registration(client, app):
    db = get_db(app)
    delete_user(db, user)
    
    rv = registrate(client, user['name'], user['email'], user['password'])
    assert b"Your registration was succesfull" in rv.data

def test_login(client):
    rv = login(client, user['email'], user['password'])
    assert b"You logged in succesfully" in rv.data

def test_logout(client):
    rv = logout(client)
    assert b"You are not logged in now" in rv.data

def test_wrong_login(client):
    rv = login(client, user['email']+'meh', user['password'])
    assert b"Invalid email or password" in rv.data

    rv = login(client, user['email'], user['password']+'meh')
    assert b"Invalid email or password" in rv.data



