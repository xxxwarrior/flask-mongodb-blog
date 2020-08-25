from math import ceil
import os

from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, \
                  redirect, url_for, session, flash, \
                  send_from_directory
from flask_login import current_user, login_required
from mongoengine import ValidationError
from mongoengine.queryset.visitor import Q

from database import Post, User, Tag, Comment, slugify
from .forms import PostForm, CommentForm
from app import app


posts = Blueprint('posts', __name__, template_folder='templates')


file_path = app.config['UPLOAD_FOLDER'] + r'\\' 




###--- Posts interaction and projection views ---###

def make_tags(tags_str: str) -> list:
    """ Makes a list of Tag objects from a string """

    tags = [Tag(name=tag.strip()) for tag in tags_str.split(',')]
    tag_list = []
    for tag in tags: 
        if tag not in tag_list:
            tag_list.append(tag)
    return tag_list

def allowed_file(filename):
    allowed_ext = {'png', 'jpeg', 'jpg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext



#- Add new post view -#
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


#- Edit a post view -# 
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
                    with open(file_path + filename, 'rb') as f:
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


#- Posts page view -#
@posts.route('/')
def index():
    q = request.args.get('q')
    page = request.args.get('page')

    print(current_user.is_authenticated)


    if page and page.isdigit():
        page = int(page)
    else: page = 1

    posts_count = Post.objects.count()
    rows_per_page = 3
    posts_per_row = 4
    posts_per_page = rows_per_page * posts_per_row
    total_pages = ceil(posts_count / posts_per_page)
    skip = (page-1) * posts_per_page
    print('skip', skip)
    print('total pages', total_pages)

    if q: 
        posts = Post.objects(Q(title__icontains=q) | 
                             Q(body__icontains=q)).order_by('-date').skip(skip).limit(posts_per_page)
    else: 
        posts = Post.objects.order_by('-date').skip(skip).limit(posts_per_page)
        posts = [post for post in posts]
        # posts = Post.objects.order_by('-date')
            

    return render_template('posts/index.html', posts=posts, rows_per_page=rows_per_page, posts_per_row=posts_per_row, page=page, totalPages=total_pages)


@posts.route('/uploads/<filename>')
def uploaded_file(filename):
    """ Downloads a file from a static directory """ 
    #-- This function is called by html template to display post picture --#
    print('>>>>>>>>>>>>>>>>>>>>>>')
    return send_from_directory(file_path, filename)


#- Post view -#
# http://localhost/blog/first-post
@posts.route('/<slug>', methods=['POST', 'GET'])
def post_detail(slug):

    try: 
        post = Post.objects(slug=slug).first()
        tags = post.tags
    
        if post.picture and post.pic_name:
            filename = post.pic_name
        else: filename = None
        try: 
            user = post.user.fetch()
            user_id = str(user.id)
        except AttributeError:
            user_id = None

        form = CommentForm()
        if current_user.is_authenticated:
            comment_author = User.objects(id=current_user.get_id()).first()
        else: comment_author = None
        if request.method == 'POST':
            comment = request.form.get('comment')
            if form.validate_on_submit: 
                comment = Comment(body=comment, author=comment_author)
                post.comments.append(comment)
                post.save()

        return render_template('posts/post_detail.html', post=post, tags=tags, picture=filename, post_author=user_id, \
                                                        form=form, comments=post.comments[::-1], comment_author=comment_author)
    except Exception as e:
        print(f'fail happend: {e}, {type(e)}')
        return render_template('404.html'), 404


#- Tag search view -#
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
