# main.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


# Displays the main page (no need for authentication)
@main.route('/')
def index():
    return render_template('index.html')


# Displays the user profile (authentication is needed)
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.user_name)


