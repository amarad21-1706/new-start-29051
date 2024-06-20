from db import db
from datetime import datetime
from models.user import Post, UserRoles, Role, Users, AuditLog
from sqlalchemy.exc import IntegrityError

def get_user_roles(session=None, user_id=None):
    # Query UserRoles to get the roles for the given user ID
    user_roles = session.query(UserRoles).filter(UserRoles.user_id == user_id).all()
    # Extract role IDs from user_roles
    role_ids = [user_role.role_id for user_role in user_roles]
    # Query Role table to get role names for the extracted role IDs
    roles = session.query(Role).filter(Role.id.in_(role_ids)).all()
    # Extract role names from roles
    role_names = [role.name for role in roles]
    print('Roles for user', user_id, 'are:', role_names)
    if not role_names:
        return None
    return role_names

import sqlalchemy
from sqlalchemy.exc import IntegrityError
# import logging


def create_message(session=None, user_id=None, message_type=None, subject=None, body=None, sender=None, company_id=None,
                   lifespan='one-off', allow_overwrite=False):
    try:
        # Check if a similar message already exists
        existing_message = session.query(Post).filter_by(user_id=user_id, subject=subject,
                                                            message_type=message_type).first()

        if existing_message:
            # Handle existing message
            if allow_overwrite:
                # Update the existing message
                existing_message.body = body
                existing_message.sender = sender
                existing_message.created_at = datetime.utcnow()
                session.commit()  # Commit the transaction
                #logging.info("Message updated successfully.")
            else:
                # Append the message if overwriting is not allowed
                # logging.warning("Message already exists and overwriting is not allowed.")
                pass
        else:
            # Create a new Message instance
            message_content = Post(
                user_id=user_id,
                message_type=message_type,
                subject=subject,
                body=body,
                sender=sender,
                company_id=company_id,
                lifespan=lifespan,
                created_at=datetime.utcnow()  # Ensure UTC datetime
            )
            # Add the message to the session
            session.add(message_content)
            session.commit()  # Commit the transaction
            #logging.info("Message created successfully.")

    except IntegrityError as e:
        session.rollback()  # Rollback the transaction
        #logging.error("Integrity error occurred while creating message: %s", str(e))

    except sqlalchemy.exc.SQLAlchemyError as e:
        session.rollback()  # Rollback the transaction
        # logging.error("Error occurred while creating message: %s", str(e))

    except Exception as e:
        session.rollback()  # Rollback the transaction
        # logging.error("Unexpected error occurred while creating message: %s", str(e))


# Example usage:
# create_message(session, user_id=1, message_type='last_access', subject='Last Access Notification', body='You accessed the system.', allow_overwrite=True)
# create_message(session, user_id=1, message_type='email', subject='New Notification', body='You have a new notification.')


# Example usage:
# Assuming you have an active SQLAlchemy session named 'session'
# create_message(session, user_id=1, message_type='email', subject='New Notification', body='You have a new notification.')



def generate_menu_tree(menu, depth=0):
    """
    Recursively generates a clean tree from the menu structure.

    Args:
    - menu (dict): The menu structure.
    - depth (int): The depth of the current recursion.

    Returns:
    - str: The generated tree as a string.
    """
    tree = ""
    # Indentation based on the depth
    indentation = "  " * depth

    for key, value in menu.items():
        # Skip the "url" and "protected" keys
        if key not in ["url", "protected"]:
        #if key not in ["url"]:

            # Append the current label to the tree
            tree += f"{indentation}- {value['label']}\n"

            # Recursively process submenus
            if "submenus" in value:
                tree += generate_menu_tree(value["submenus"], depth + 1)

    return tree
