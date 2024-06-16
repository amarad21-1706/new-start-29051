from flask import render_template, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from app.models.user import Users
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from app.modules.db import db
from app.app_factory import create_app

app = create_app()
db.init_app(app)

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

def reset_password(username, new_password):
    user = Users.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        print(f"Password for user {username} has been reset.")
    else:
        print(f"No user found with username {username}.")

class AdminResetPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

@app.route('/admin_reset_password', methods=['GET', 'POST'])
def admin_reset_password():
    form = AdminResetPasswordForm()
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        reset_password(username, new_password)
        flash('Password has been reset for the user.', 'success')
        return redirect(url_for('index'))
    return render_template('admin_reset_password.html', form=form)

@app.route('/')
def index():
    form = AdminResetPasswordForm()
    return render_template('admin_reset_password.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
