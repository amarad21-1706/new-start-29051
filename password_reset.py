from flask import Blueprint, render_template, flash, redirect, url_for, request
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo
from flask_login import login_required, current_user
from models.user import Users
from db import db

password_reset_bp = Blueprint('password_reset', __name__)

class AdminResetPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

class UserChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')



@password_reset_bp.route('/admin_reset_password', methods=['GET', 'POST'])
@login_required
def admin_reset_password_route():
    form = AdminResetPasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        new_password = form.password.data
        reset_password_adm(username, new_password)
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')
        return render_template('admin_reset_password.html', form=form)

@password_reset_bp.route('/user_change_password', methods=['GET', 'POST'])
@login_required
def user_change_password_route():
    form = UserChangePasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data

        if current_user.check_password(current_password):
            reset_password(current_user, new_password)
            return redirect(url_for('index'))
        else:
            flash('Current password is incorrect.', 'danger')

    return render_template('user_change_password.html', form=form)


def reset_password_adm(username, new_password):
    user = Users.query.filter_by(username=username).first()
    if user:
        user.set_password(new_password)
        db.session.commit()
        flash(f"Password for user {username} has been reset.", 'success')
    else:
        flash(f"No user found with username {username}.", 'danger')

def reset_password(user, new_password):
    user.set_password(new_password)
    db.session.commit()
    flash(f"Password has been changed successfully.", 'success')

