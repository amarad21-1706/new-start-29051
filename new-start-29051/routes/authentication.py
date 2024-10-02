# app/routes/authentication.py
from flask import current_app, redirect, render_template, url_for, flash
from flask_login import login_user
from flask import Blueprint

from userManager101 import UserManager
from app import app, bcrypt

user_manager = UserManager()
authentication = Blueprint('authentication', __name__)

@app.route('/access/login', methods=['GET', 'POST'])
def login():
    # ... (move the login route code here)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = user_manager.authenticate_user(username, password)

        if user:
            login_user(user)
            flash('Login Successful')
            return redirect(url_for('index'))  # Redirect to the home page upon successful login
        else:
            flash('Login Failed')
            return redirect(url_for('login'))

    return render_template('access/login.html')