from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect, url_for
from flask_security import login_required


from mongoengine.queryset.visitor import Q

from math import ceil

from database import Post # db, 

from .forms import PostForm

posts = Blueprint('posts', __name__, template_folder='templates')


# http://localhost/blog/create
@posts.route('/create', methods=['POST', 'GET'])
@login_required
def create_post(): 

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        try:
            Post(title=title, body=body).save()
        except:
            print("Something went wrong")
        
        return redirect(url_for('posts.index'))


    form = PostForm()
    return render_template('posts/create_post.html', form=form)




# TODO do smth with form it should be filled with current title etc

@posts.route('/edit/<slug>', methods=['POST', 'GET'])
@login_required
def edit_post(slug):
    try: 
        post = Post.objects(slug=slug)

        if request.method == 'POST':
            title = request.form.get('title')
            body = request.form.get('body')

            try:
                post.update(title=title, body=body)
            except:
                print("Something went wrong")
        
            return redirect(url_for('posts.post_detail', slug=post['slug']))
        
        form = PostForm(obj=post)
        return render_template('posts/edit_post.html', post=post, form=form)
    except IndexError:
        return render_template('404.html'), 404




@posts.route('/')
def index():

    q = request.args.get('q')
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else: page = 1

    total_posts = Post.objects.count()
    posts_per_page = 5
    total_pages = ceil(total_posts / posts_per_page)
    skip = (page-1) * posts_per_page

    if q: 
        posts = Post.objects(Q(title__icontains=q) | 
                    Q(body__icontains=q)).order_by('date').skip(skip).limit(posts_per_page)
    else: 
        posts = Post.objects.order_by('date').skip(skip).limit(posts_per_page)

    return render_template('posts/index.html', posts=posts, page=page, totalPages=total_pages)


# http://localhost/blog/first-post
@posts.route('/<slug>')
def post_detail(slug):
    try: 
        post = Post.objects(slug=slug).first()
        tags = post.tags
        return render_template('posts/post_detail.html', post=post, tags=tags)
    except:
        return render_template('404.html'), 404

# http://localhost/blog/tag/fuck
@posts.route('/tag/<slug>')
def tag_detail(slug):
    try: 
        posts = Post.objects(tags__match={'slug': slug})
        tag = posts[0].tags.get(slug=slug)
        return render_template('posts/tag_detail.html', tag=tag, posts=posts)
    except:
        return render_template('404.html'), 404
