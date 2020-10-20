# This script allow the authentication forms for this API
# In this way there is not direct access to the implementation

# General imports:
import traceback

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from flask_login import LoginManager

# custom imports:
from settings import initial_settings as init

# Blueprint for the authentication section
auth = Blueprint('auth', __name__)
log = init.LogDefaultConfig("auth.log").logger


# GET for Login
@auth.route('/login')
def login():
    return render_template('login.html')


# POST for login
@auth.route('/login', methods=['POST'])
def login_post():
    # check if after the login, it needs to be redirected
    # if '?next=' in request.referrer:
    #    next_url = request.referrer.split('?next=')[1]
    #    next_url = next_url.replace("%2F", "/")
    # else:
    #    next_url = None

    try:
        identification = request.form.get('identification')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        next_url = request.form.get("next")

        user = User.query.filter_by(email=identification).first()
        if not user:
            user = User.query.filter_by(user_name=identification).first()

        # check if user actually exists
        # take the user supplied password, hash it, and compare it to the hashed password in database
        if not user or not user.check_password(password):
            flash('Por favor revise sus credenciales, no se ha podido validar esta sesión.')
            return redirect(url_for('auth.login'))  # if user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)

        # if there is a URL to redirect then go ahead
        if next_url:
            return redirect(next_url)
        return redirect(url_for('main.profile'))
    except Exception as e:
        msg = "Error when running the login process. Check the log file 'auth.log' for more details"
        tb = traceback.extract_stack()
        log.error(f"{msg} \n{str(e)} \n{tb}")
        return dict(success=False, msg=msg), 500


# GET for signup (if it applies)
@auth.route('/signup')
def signup():
    return render_template('signup.html')


# POST for signup (if it applies)
@auth.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # If email has already used
    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(email=email).first()

    # if a user is found, we want to redirect back to signup page so user can try again
    if user:
        flash('El correo electrónico ya ha sido usado por otro usuario')
        return redirect(url_for('auth.signup'))

    # If user name has already used
    # if this returns a user, then the user_name already exists in database
    user = User.query.filter_by(user_name=name).first()

    # if a user is found, we want to redirect back to signup page so user can try again
    if user:
        flash('El correo electrónico ya ha sido usado por otro usuario')
        return redirect(url_for('auth.signup'))

    # create new user with the form data
    new_user = User(email=email, user_name=name, password=password)
    # add the new user to the database
    new_user.commit()

    return redirect(url_for('auth.login'))


# GET for logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# this function allows to add authentication to the API
# this function should be called after the DB configuration
def add_authentication(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # This callback is used to reload the user object from the user ID stored in the session.
    # It should take the unicode ID of a user, and return the corresponding user object
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        # this method runs inside the server, therefore no user_id is exposed
        return User.query.get(int(user_id))


# This is a decorator function. It allows the access to routes depending on the rights of the user
# using this wrapper a token from the user is mandatory otherwise
# no access is allowed
from functools import wraps
from flask import request
import jwt
# import global configurations:
from settings import initial_settings as init
from dto.sqlite_engine_handler.Users import User


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return dict(success=False, msg='Token no incluído'), 401
        # if the token is in the request:
        try:
            data = jwt.decode(token, init.SECRET_KEY)
            current_user = User.query.filter_by(public_id=data['public_id']).first()
            return f(current_user, *args, **kwargs)
        except:
            return dict(success=False, msg="Token invalido"), 401

    return decorated