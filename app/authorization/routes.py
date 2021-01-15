from flask import url_for, render_template, \
                  request, redirect, flash
from flask_login import current_user, login_user, logout_user
from mongoengine.errors import NotUniqueError

from app import login_manager
from app.authorization import auth_bp
from app.database import User
from .forms import LoginForm, RegisterForm



@login_manager.user_loader
def user_loader(user_id):
    user = User.objects(id=user_id).first()
    if user:
        return user
    return



flashes = {
    "invalid": "Invalid email or password!",
    "login": "You logged in succesfully!",
    "registered": "Your registration was succesfull!",
    "notUnique": "This email is already registered!",
    "error": "An error occured, please try again later.",
    "logout": "You are not logged in now!"
}


@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        
        if form.validate_on_submit:  
            user = User.objects(email=form.email.data).first()
            
            if not user:
                flash(flashes["invalid"], "error")
                return render_template('authorization/login.html', login_user_form=form)
            elif user.check_password(form.password.data) == False:
                flash(flashes["invalid"], "error")
                return render_template('authorization/login.html', login_user_form=form)
            
            login_user(user)
            flash(flashes["login"])   

        return redirect(url_for('posts_bp.index'))
        
    return render_template('authorization/login.html', login_user_form=form)
    

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST': 
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            usr = User(name=name, email=email)
            usr.set_password(password)
            usr.save()
            flash(flashes["registered"])
            return redirect('/login')
        except NotUniqueError:
            flash(flashes["notUnique"], "error")
        except Exception:
            flash(flashes["error"])
    form = RegisterForm()
    return render_template('authorization/register.html', form=form)


@auth_bp.route('/logout')
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    flash(flashes["logout"])
    return redirect(url_for('posts_bp.index'))



