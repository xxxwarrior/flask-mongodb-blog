# Flask + MongoDB + Bootstrap + JS + Docker Compose


This is a blog-like application, which allows authenticated users to create posts with pictures and tags attached, edit and delete those posts. The posts can be commented. There's an admin view, where you can see all the posts and edit them easily. You can search for a specific post via search bar or search by tags. 

## Installation 
### Docker 
Docker is required
1. `git clone https://github.com/xxxwarrior/flask-mongodb-blog.git`
2. `cd flask-mongodb-blog`
3. `docker-compose build`
4. `docker-compose up`

### Locally
Python and MongoDB are required
1. `git clone https://github.com/xxxwarrior/flask-mongodb-blog.git`
2. `cd flask-mongodb-blog`
* (Optionally) Create a virtual env
```
python -m venv env
source env/Scripts/activate
```
3. `pip install -r requirements.txt`
4. Create `.env` file with the following content
```
DB_URI = "mongodb://localhost:27017"
UPLOAD_FOLDER = "path\\to\\upload\\folder"
SECRET_KEY = "Super secret key"	
SALT = 'salt'
```
Notes: DB_URI *may vary, e.g. Atlas URI may be used*, UPLOAD_FOLDER *is used to store the pictures attached to the app posts*, SECRET_KEY *and* SALT *are necessary for Flask Security*. 

5. `python main.py`

