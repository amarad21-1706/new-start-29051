# master_password_reset.py

from flask import render_template, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from db import db
from models.user import Users

class PasswordResetManager:
    def authenticate_user(self, username, password):
        print(f"Authenticating user {username}")
        user = Users.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}")
            if check_password_hash(user.password, password):
                print("Password check passed")
                return user
            else:
                print("Password check failed")
        else:
            print("User not found")
        return None


class AdminResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


def reset_password(username, new_password):
    user = Users.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        print(f"Password for user {username} has been reset.")
    else:
        print(f"No user found with username {username}.")


def admin_reset_password():
    form = AdminResetPasswordForm()
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        reset_password(username, new_password)
        flash('Password has been reset for the user.', 'success')
        return redirect(url_for('index'))
    return render_template('admin_reset_password.html', form=form)
