from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect, url_for
from flask_security import login_required

from math import ceil

from database import db, Post

from .forms import PostForm

posts = Blueprint('posts', __name__, template_folder='templates')

r = '.*'

# http://localhost/blog/create
@posts.route('/create', methods=['POST', 'GET'])
@login_required
def create_post(): 

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        try:
            post = {'title': title, 'body': body}
            post = Post(post)
            db.posts.insert_one(post.obj())
        except:
            print("Something went wrong")
        
        return redirect(url_for('posts.index'))


    form = PostForm()
    return render_template('posts/create_post.html', form=form)





@posts.route('/edit/<slug>', methods=['POST', 'GET'])
@login_required
def edit_post(slug):
    try: 
        post = db.posts.find_one({'slug': slug})

        if request.method == 'POST':
            title = request.form.get('title')
            body = request.form.get('body')

            try:
                db.posts.update_one({'slug': slug}, {'$set': {'title': title, 'body': body}})
            except:
                print("Something went wrong")
        
            return redirect(url_for('posts.post_detail', slug=post['slug']))
        
        form = PostForm(obj=post)
        return render_template('posts/edit_post.html', post=post, form=form)
    except IndexError:
        return render_template('404.html'), 404




# posts = Post.objects()

@posts.route('/')
def index():

    q = request.args.get('q')

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else: page = 1

    totalPosts = db.posts.count_documents({})
    postsPerPage = 5
    totalPages = ceil(totalPosts / postsPerPage)
    skip = (page-1) * postsPerPage
    
    if q: # This is probably can be done with creating indexed and using text search
        q = r+q+r # THis beautiful piece of code is for searching with regex
        posts = db.posts.find({'$or': 
            [{'title': {'$regex': q, '$options': 'i'}}, 
            {'body': {'$regex': q, '$options':'i'}}]}).sort('date').skip(skip).limit(postsPerPage)
    else: 
        posts = db.posts.find({}).sort('date').skip(skip).limit(postsPerPage)

    posts = list(posts)
        
    return render_template('posts/index.html', posts=posts, page=page, totalPages=totalPages)


# http://localhost/blog/first-post
@posts.route('/<slug>')
def post_detail(slug):
    try: 
        post = list(db.posts.find({ "slug": slug }))[0]
        tags = post.get('tags')
        return render_template('posts/post_detail.html', post=post, tags=tags)
    except IndexError:
        return render_template('404.html'), 404

# http://localhost/blog/tag/fuck
@posts.route('/tag/<slug>')
def tag_detail(slug):
    try: 
        posts = list(db.posts.find({'tags': {'$elemMatch': {'slug': slug}}}))
        tag = [tag for tag in posts[0]['tags'] if tag['slug'] == slug][0]
        return render_template('posts/tag_detail.html', tag=tag, posts=posts)
    except IndexError:
        return render_template('404.html'), 404
