from flask_bcrypt import check_password_hash
from models.user import Users
from flask import current_app
from flask import session
from flask_login import UserMixin
from sqlalchemy.orm import joinedload
from flask_login import current_user

from flask_sqlalchemy import SQLAlchemy
class UserManager:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def manage_users(self):
        # Implement the user management logic here
        print("Managing users... implement logic here")

    def authenticate_user222(self, username, password):
        try:
            print('auth', username, password)
            user = Users.query.filter_by(username=username).options(joinedload(Users.roles)).first()
            print('user', user)
            if user and check_password_hash(user.password_hash, password):
                print('checked ok', user)
                session['user_id'] = user.id
                session['username'] = user.username
                print('just logged in', user.id, user.username, user)

                return user
            else:
                print('not logged in!')

                return None
        except Exception as e:
            print(f'Db error (4): {e}')
            return None


    def authenticate_user(self, username, password):
        try:
            print('auth', username, password)
            user = Users.query.filter_by(username=username).options(joinedload(Users.roles)).first()
            print('user', user)
            if user and check_password_hash(user.password_hash, password):
                print('checked ok', user)
                session['user_id'] = user.id
                session['username'] = user.username
                session['roles'] = [role.name for role in user.roles]
                print('roles', session['roles'])
                print('just logged in', user.id, user.username, user)
                return user
            else:
                print('not logged in!')
                session['user_id'] = None
                session['username'] = 'guest'
                session['roles'] = ['guest']
                return None
        except Exception as e:
            print(f'Db error (4): {e}')
            session['user_id'] = None
            session['username'] = 'guest'
            session['roles'] = ['guest']
            return None


    def load_user(self, user_id):
        # Check if user_id is not None and is a string representation of an integer
        if user_id is not None:
            # Load user from the database using user_id
            user_data = Users.query.get(int(user_id))
            # print('user id', user_data.id, ', roles', user_data.roles)
            return user_data  # Return the actual Users object if found, else None
        return None  # Return None if user_id is None or not a valid integer string


    def load_user_by_username(self, username):
        try:
            from app.modules.db import db
            current_app.logger.info(f'***Loading user by username***: {username}')
            user_instance = db.Users.query.filter_by(username=username).first()
            # Commit the session if necessary
            db.session.commit()
            return user_instance
        except Exception as e:
            print(f'Db error 4 (load_user_by_username): {e}')
            raise
            return None



class TemporaryUser(UserMixin):
    def __init__(self, user_id, username="Guest"):
        self.id = user_id
        self.user_name = username
    @property
    def is_active(self):
        return True

    # Add a setter for is_active
    @is_active.setter
    def is_active(self, value):
        pass

    def get_id(self):
        return str(self.id)


class Usr(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        self.user_name = username
        self.is_active = True

    # Override the get_id method to return a string
    def get_id(self):
        user_id_str = str(self.id)
        print(f"get_id called. Returning: {user_id_str[:3]}")
        return user_id_str

    # You can use @property to define a property
    @property
    def username(self):
        username = session.get('username', '')
        return username


    @property
    def greeting_message(self):
        return f"Hello, {self.user_name}!"


def check_role(required_role, allowed_roles):
    """
    Check if the current user has the required role among the allowed roles.

    Parameters:
    - required_role (str): The role required to access a particular route.
    - allowed_roles (list): The list of roles allowed to access a particular route.

    Returns:
    - bool: True if the user has the required role, False otherwise.
    """
    # print("Checking role; required vs current", required_role, current_user.roles)
    return current_user.is_authenticated and required_role in current_user.roles and required_role in allowed_roles
