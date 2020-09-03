from flask import Blueprint, url_for, render_template, \
                  request, session, redirect, flash

from flask_login import current_user, login_user, logout_user

from mongoengine.errors import NotUniqueError

from .forms import LoginForm, RegisterForm
from database import User
from app import bcrypt, login_manager



authorization = Blueprint('authorization', __name__, template_folder='templates')


@login_manager.user_loader
def user_loader(user_id):
    user = User.objects(id=user_id).first()
    if user:
        return user
    return

@authorization.route('/login', methods=['POST', 'GET'])
def login():
    print('Im here')
    form = LoginForm()
    if request.method == 'POST':
        print('>>form errors', form.errors)
        
        if form.validate_on_submit:  
            user = User.objects(email=form.email.data).first()
            print('>>>', user)
            if not user:
                flash("Invalid email or password", "error")
                return render_template('authorization/login.html', login_user_form=form)
            elif bcrypt.check_password_hash(user.password, form.password.data) == False:
                flash("Invalid email or password", "error")
                return render_template('authorization/login.html', login_user_form=form)
                        
            print('cheking', bcrypt.check_password_hash(user.password, form.password.data))
            print(user.password)
            login_user(user)
            flash("You logged in succesfully")   

        return redirect(url_for('posts.index'))
        
    return render_template('authorization/login.html', login_user_form=form)
    

@authorization.route('/register', methods=['GET', 'POST'])
def register():
    print('yo')
    if request.method == 'POST': 
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            pw_hash = bcrypt.generate_password_hash(password)
            usr = User(name=name, email=email, password=pw_hash)
            usr.save()
            flash("Your registration was succesfull")
            return redirect('/login')
        except NotUniqueError:
            flash("This email is already registered", "error")
        except Exception as e:
            print(e)
            print(type(e))
    form = RegisterForm()
    return render_template('authorization/register.html', form=form)


@authorization.route('/logout')
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    flash("You are not logged in now")
    return redirect(url_for('posts.index'))



