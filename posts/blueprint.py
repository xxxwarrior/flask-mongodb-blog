from math import ceil

from werkzeug.local import LocalProxy
from flask import Blueprint, render_template, request, \
                    redirect, url_for, session, flash
from flask_security import login_required

from mongoengine.queryset.visitor import Q
from mongoengine import ValidationError

from database import Post, User, Tag, slugify
from .forms import PostForm


posts = Blueprint('posts', __name__, template_folder='templates')


def make_tags(tags_str: str) -> list:
    tags = [Tag(name=tag.strip()) for tag in tags_str.split(',')]
    new_tags = []
    for tag in tags: 
        if tag not in new_tags:
            new_tags.append(tag)
    return new_tags


# http://localhost/blog/create
@posts.route('/create', methods=['POST', 'GET'])
@login_required
def create_post(): 
    form = PostForm()

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        tags = request.form.get('tags')
        user = User.objects(id=session.get('_user_id')).first()
        try:
            post = Post(title=title, body=body, user=user)
            if tags:
                    post.tags = make_tags(tags)
                    post.save()
        except Exception as e:
            print(f"Something went wrong: {e}")
            flash("An error occured, please try again", "error")
            return render_template('posts/create_post.html', form=form)
        
        flash("Your post has been successfully created", "message")
        return redirect(url_for('posts.index'))

    return render_template('posts/create_post.html', form=form)



# TODO Access only to the user's posts
@posts.route('/edit/<slug>', methods=['POST', 'GET'])
@login_required
def edit_post(slug):
    try: 
        post = Post.objects(slug=slug).first()
        form = PostForm(obj=post)
        
        
        if request.method == 'POST':
            title = request.form.get('title')
            body = request.form.get('body')
            tags = request.form.get('tags')
            try:
                post.update(title=title, slug=slugify(title), body=body)
                if tags:
                    post.tags = make_tags(tags)
                    post.save() 
            except ValidationError:
                flash("The title is too long, please try again", "error")
                return render_template('posts/edit_post.html', post=post, tags=tags, form=form)
            except Exception as e:
                flash("An error occured, please try again", "error")
                print(f"Something went wrong: {e}, type: {type(e)}")
                return render_template('posts/edit_post.html', post=post, tags=tags, form=form)

            flash("You've edited your post successfully", "message")
            return redirect(url_for('posts.index'))

        if post.tags:
            tags = ', '.join([tag.name for tag in post.tags])
        else: tags=""
        return render_template('posts/edit_post.html', post=post, tags=tags, form=form)

    except Exception as e:
        print(f'>>> {e}')
        flash("An error occured, please try again", "error")
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
    except Exception as e:
        print(f">>>{e}")
        return render_template('404.html'), 404
