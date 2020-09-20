from math import ceil
import os

from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from flask import render_template, request, redirect, \
                  url_for, flash, send_from_directory,\
                  current_app
from flask_login import current_user, login_required
from mongoengine import ValidationError
from mongoengine.queryset.visitor import Q

from app.database import Post, User, Tag, Comment, slugify
from .forms import PostForm, CommentForm
from app.posts import posts_bp



def make_tags(tags_str: str) -> list:
    """ Makes a list of Tag objects from a string """

    tags = [Tag(name=tag.strip()) for tag in tags_str.split(',')]
    tag_list = []
    for tag in tags: 
        if tag not in tag_list:
            tag_list.append(tag)
    return tag_list


def is_allowed_file(filename):
    allowed_ext = {'png', 'jpeg', 'jpg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


# For now it's for pics only, might remake later
def attach_file(post, file):
    """ Saves a file into an upload folder and attaches the file to a post """

    filename = secure_filename(file.filename)
    post.pic_name = filename
    file_path = current_app.config['UPLOAD_FOLDER'] + r'\\'
    file.save(os.path.join(file_path, filename))
    with open(file_path + filename, 'rb') as f:
        post.picture.put(f, content_type='image/jpeg')

flashes = {
    'error': "An error occured, please try again later.",
    'badformat': "The file format is not supported.",
    'nofile': "The file was not selected."
}

#-/ Add new post view \-#
# http://localhost/blog/create
@posts_bp.route('/create', methods=['POST', 'GET'])
@login_required
def create_post(): 
    form = PostForm()

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        tags = request.form.get('tags')
        file = request.files.get('file')
        user = User.objects(id=current_user.get_id()).first()
        try:
            post = Post(title=title, body=body, user=user)
            if tags:
                    post.tags = make_tags(tags)
            if file: 
                filename = file.filename
                if not is_allowed_file(filename):
                    flash(flashes['badformat'])
                elif filename == '':
                    flash(flashes['nofile'], "error")
                attach_file(post, file)
            else: filename = None
            post.save()
        except Exception:
            flash(flashes['error'], "error")
            return render_template('posts/create_post.html', form=form)
        
        flash("Your post has been successfully created", "message")
        return redirect(url_for('posts_bp.index'))

    return render_template('posts/create_post.html', form=form)



#-/ Edit a post view \-# 

#TODO This document already has a file. Either delete it or call replace to overwrite it, type: <class 'mongoengine.fields.GridFSError'> 
@posts_bp.route('/edit/<slug>', methods=['POST', 'GET'])
@login_required
def edit_post(slug):
    try: 
        post = Post.objects(slug=slug).first()
        form = PostForm(obj=post)
        
        if request.method == 'POST':
            title = request.form.get('title')
            body = request.form.get('body')
            tags = request.form.get('tags')
            file = request.files.get('file')
            try:
                post.update(title=title, slug=slugify(title), body=body)
                if tags:
                    post.tags = make_tags(tags)
                if file:
                    filename = file.filename
                    if not is_allowed_file(filename):
                        flash(flashes['badformat'])
                    elif filename == '':
                        flash(flashes['nofile'], "error")
                    
                    attach_file(post, file)
                post.save() 
            except ValidationError:
                flash("An error occured. The title might be too long.", "error")
                return render_template('posts/edit_post.html', post=post, tags=tags, form=form)
            except Exception:
                flash(flashes['error'], "error")
                return render_template('posts/edit_post.html', post=post, tags=tags, form=form)

            flash("You've edited your post successfully", "message")
            return redirect(url_for('posts_bp.post_detail', slug=post.slug))

        if post.tags:
            tags = ', '.join([tag.name for tag in post.tags])
        else: tags=""
        return render_template('posts/edit_post.html', post=post, tags=tags, form=form)

    except Exception:
        flash(flashes['error'], "error")
        return render_template('404.html'), 404


#-/ Posts page view \-#
@posts_bp.route('/')
def index():
    q = request.args.get('q')
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else: page = 1

    posts_count = Post.objects.count()
    rows_per_page = 3
    posts_per_row = 4
    posts_per_page = rows_per_page * posts_per_row
    total_pages = ceil(posts_count / posts_per_page)
    skip = (page-1) * posts_per_page

    if q: 
        posts = Post.objects(Q(title__icontains=q) | 
                             Q(body__icontains=q)).order_by('-date').skip(skip).limit(posts_per_page)
    else: 
        posts = Post.objects.order_by('-date').skip(skip).limit(posts_per_page)
        # when passed to a template, posts queryset contains not just needed objects but all of them
        # that is why it's nessesary to make a deep copy of the expected slice:
        posts = [post for post in posts]
            
    return render_template('posts/index.html', posts=posts, rows_per_page=rows_per_page, posts_per_row=posts_per_row, page=page, totalPages=total_pages)


@posts_bp.route('/uploads/<filename>')
def download_file(filename):
    """ Downloads a file from a static directory """ 
    #-- This function is called by html template to display post picture --#

    file_path = current_app.config['UPLOAD_FOLDER'] + r'\\' 
    return send_from_directory(file_path, filename)


#-/ Post view \-#
# http://localhost/blog/first-post
@posts_bp.route('/<slug>', methods=['POST', 'GET'])
def post_detail(slug):
    try: 
        post = Post.objects(slug=slug).first()
        tags = post.tags if post.tags else []
    
        if post.picture and post.pic_name:
            filename = post.pic_name
        else: filename = None
        try: 
            user = post.user.fetch()
            user_id = str(user.id)
        except Exception:
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
                                                        form=form, comment_author=comment_author, comments=post.comments[::-1])
    except Exception:
        return render_template('404.html'), 404


#-/ Tag search view \-#
# http://localhost/blog/tag/sometag
@posts_bp.route('/tag/<slug>')
def tag_detail(slug):
    try: 
        posts = Post.objects(tags__match={'slug': slug})
        tag = posts[0].tags.get(slug=slug)
        return render_template('posts/tag_detail.html', tag=tag, posts=posts)
    except Exception:
        return render_template('404.html'), 404


@posts_bp.route('/<slug>/delete-comment/<comment_id>')
def delete_comment(slug, comment_id):
    try:
        post = Post.objects(slug=slug).first()
        comment_id = ObjectId(comment_id)
        post.update(pull__comments__oid=comment_id)
        post.save()
    except Exception:
        flash(flashes['error'], 'error')
    return redirect(url_for('posts_bp.post_detail', slug=slug))
