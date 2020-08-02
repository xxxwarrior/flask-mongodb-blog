from math import ceil
import os

from werkzeug.local import LocalProxy
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, \
                  redirect, url_for, session, flash, \
                  send_from_directory
                    
from flask_security import login_required
from flask_login import current_user

from mongoengine.queryset.visitor import Q
from mongoengine import ValidationError

from database import Post, User, Tag, slugify
from .forms import PostForm
from app import app


posts = Blueprint('posts', __name__, template_folder='templates')
file_path = app.config['UPLOAD_FOLDER'] + r'\\' 


def make_tags(tags_str: str) -> list:
    tags = [Tag(name=tag.strip()) for tag in tags_str.split(',')]
    new_tags = []
    for tag in tags: 
        if tag not in new_tags:
            new_tags.append(tag)
    return new_tags

def allowed_file(filename):
    allowed_ext = {'png', 'jpeg', 'jpg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext



# http://localhost/blog/create
@posts.route('/create', methods=['POST', 'GET'])
@login_required
def create_post(): 
    form = PostForm()

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        tags = request.form.get('tags')
        
        user = User.objects(id=current_user.get_id()).first()
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
            file = request.files['file']
            filename = request.files['file'].filename
           

            print(f">>> file: {request.files['file']}")
            print(f">>> filename: {request.files['file'].filename}")
            
        
            try:
                post.update(title=title, slug=slugify(title), body=body)
                if tags:
                    post.tags = make_tags(tags)
                if file:
                    if not allowed_file(filename):
                        flash("The file format is not supported", "error")
                    elif filename == '':
                        flash("No selected file", "error")

                    filename = secure_filename(filename)
                    post.pic_name = filename
                    file.save(os.path.join(file_path, filename))
                    with open(file_path+filename, 'rb') as f:
                        post.picture.put(f, content_type='image/jpeg')
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

    print(current_user.get_id())

    return render_template('posts/index.html', posts=posts, page=page, totalPages=total_pages)


@posts.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(file_path, filename)




# http://localhost/blog/first-post
@posts.route('/<slug>')
def post_detail(slug):
    try: 
        post = Post.objects(slug=slug).first()
        tags = post.tags
        if post.picture and post.pic_name:
            filename = post.pic_name
            print(filename)
        try: 
            user = post.user.fetch()
            user_id = str(user.id)
        except AttributeError:
            user_id = None

        return render_template('posts/post_detail.html', post=post, tags=tags, picture=filename, author_id=user_id)
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
