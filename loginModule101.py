from flask_bcrypt import check_password_hash
from flask import current_app
from flask import session

class UserManager:
    def authenticate_user(self, username, password):
        try:
            from app.modules.db import users  # Import inside the function to avoid circular import
            current_app.logger.info(f'Attempting to authenticate user: {username} with password: {password}')
            user = user.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                return user
            else:
                return None
        except Exception as e:
            print(f'Db error ( 3 ): {e}')
            return None


