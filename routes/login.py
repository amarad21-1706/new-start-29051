# app/routes/login.py
from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash
from flask import current_app, redirect, render_template, url_for, flash
from flask_login import login_user
from db import db
from userManager101 import UserManager, Usr

user_manager = UserManager(db)

login = Blueprint('login', __name__)

# Function to print routes

@login.route('/access/login', methods=['GET', 'POST'])
def login_route():
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
    return "login.html"
    #return render_template('login.html')  # Replace with your actual template