from flask import render_template, flash, redirect, url_for, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

from flask_login import login_required, current_user
from functools import wraps
from models.user import Users
from db import db
from app_factory import create_app

app = create_app()

def roles_required(*required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_roles' in session and any(role.lower() in [r.lower() for r in session['user_roles']] for role in required_roles):
                return func(*args, **kwargs)
            else:
                flash("You do not have the necessary permissions to access this page.", "danger")
                return redirect(request.referrer or url_for('index'))
        return wrapper
    return decorator

class PasswordResetManager:
    def authenticate_user(self, username, password):
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

class AdminResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

def reset_password(username, new_password):
    user = Users.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        print(f"Password for user {username} has been reset.")
    else:
        print(f"No user found with username {username}.")

@app.route('/admin_reset_password', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def admin_reset_password_route():
    form = AdminResetPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = request.form.get('username')
        new_password = form.password.data
        reset_password(username, new_password)
        flash('Password has been reset for the user.', 'success')
        return redirect(url_for('index'))
    return render_template('admin_reset_password.html', form=form)

@app.route('/index')
def index():
    return "Home Page"

if __name__ == '__main__':
    app.run(debug=True)
