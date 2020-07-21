from math import ceil

from werkzeug.local import LocalProxy
from flask import Blueprint, render_template, request, \
                    redirect, url_for, session
from flask_security import login_required

from mongoengine.queryset.visitor import Q

from database import Post, User
from .forms import PostForm


posts = Blueprint('posts', __name__, template_folder='templates')


# TODO userfriendly behavior in case if smth goes wrong
# http://localhost/blog/create
@posts.route('/create', methods=['POST', 'GET'])
@login_required
def create_post(): 
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        user = User.objects(id=session.get('_user_id')).first()

        try:
            Post(title=title, body=body, user=user).save()
        except Exception as e:
            print(f"Something went wrong: {e}")
        
        return redirect(url_for('posts.index'))

    form = PostForm()
    return render_template('posts/create_post.html', form=form)



# TODO Make some page for the case when update went wrong
# TODO Access only to the user's posts

@posts.route('/edit/<slug>', methods=['POST', 'GET'])
@login_required
def edit_post(slug):
    try: 
        post = Post.objects(slug=slug).first()

        if request.method == 'POST':
            title = request.form.get('title')
            body = request.form.get('body')

            try:
                post.update(title=title, body=body)
            except:
                print("Something went wrong")

            return redirect(url_for('posts.index'))

        form = PostForm(obj=post)
        return render_template('posts/edit_post.html', post=post, form=form)
    except Exception as e:
        print(f'>>> {e}')
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
                             Q(body__icontains=q)).order_by('-date').skip(skip).limit(posts_per_page)
    else: 
        posts = Post.objects.order_by('-date').skip(skip).limit(posts_per_page)
        # print(type(current_user))
        print(session.get('_user_id'))

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
