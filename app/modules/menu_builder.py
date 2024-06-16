# app/modules/menu_builder.py
from pathlib import Path
import json
from app.utils.utils import get_current_directory
from jinja2.runtime import Undefined

class MenuBuilder:
    def __init__(self, menu_data, allowed_roles=None):
        self.menu_data = menu_data
        self.allowed_roles = allowed_roles or []

    def generate_menu(self, user_roles=None, is_authenticated=False, include_protected=False):
        menu_items = self.parse_menu_data(user_roles=user_roles, is_authenticated=is_authenticated, include_protected=include_protected)
        return menu_items

    def parse_menu_data(self, user_roles=None, is_authenticated=False, include_protected=False, raw_menu_data=None):
        if raw_menu_data is None:
            raw_menu_data = self.menu_data

        menu_items = []

        if isinstance(raw_menu_data, dict):
            for menu_item_name, menu_item_data in raw_menu_data.items():
                if not isinstance(menu_item_data, dict):
                    continue

                label = menu_item_data.get('label', None)  # Replace Undefined with None
                url = menu_item_data.get('url', None)  # Replace Undefined with None
                protected = menu_item_data.get('protected', False)
                allowed_roles = menu_item_data.get('allowed_roles', [])

                # Skip undefined values during serialization
                if any(value is Undefined for value in (label, url, protected, allowed_roles)):
                    continue

                # Check if the menu item is protected and the user is not authenticated
                if protected and not is_authenticated and include_protected:
                    continue

                # Check if the user has the required role to access this menu item
                # INCLUDE IF ALLOWED = 'All'
                if user_roles and not any(role in allowed_roles for role in user_roles):
                    continue

                # Recursively parse submenus
                submenus = menu_item_data.get('submenus', {})
                if not user_roles:
                    user_roles = ['Guest']
                if not allowed_roles:
                    allowed_roles = ['Guest']
                parsed_submenus = self.parse_menu_data(user_roles=user_roles,
                                                       is_authenticated=is_authenticated,
                                                       include_protected=include_protected,
                                                       raw_menu_data=submenus)

                menu_items.append({
                    'label': label,
                    'url': url,
                    'protected': protected,
                    'allowed_roles': allowed_roles,
                    'user_roles': user_roles,
                    'submenus': parsed_submenus
                })
            return menu_items

        elif isinstance(raw_menu_data, list):  # Handle the case where submenus is a list
            for menu_item_data in raw_menu_data:
                parsed_submenus = self.parse_menu_data(user_roles=user_roles,
                                                       is_authenticated=is_authenticated,
                                                       include_protected=include_protected,
                                                       raw_menu_data=menu_item_data.get('submenus', {}))

                if not user_roles:
                    user_roles = ['Guest']
                allowed_roles = menu_item_data.get('allowed_roles', [])
                if not allowed_roles:
                    allowed_roles = ['Guest']
                menu_items.append({
                    'label': menu_item_data.get('label'),
                    'url': menu_item_data.get('url'),
                    'protected': menu_item_data.get('protected', False),
                    'allowed_roles': allowed_roles,
                    'user_roles': user_roles,
                    'submenus': parsed_submenus
                })

            return menu_items
        else:
            return raw_menu_data

if __name__ == '__main__':
    # Load menu items from JSON file
    json_file_path = get_current_directory() + '/static/js/menuStructure101.json'
    with open(Path(json_file_path), 'r') as file:
        main_menu_items = json.load(file)

    # Example usage for Guest role during login
    # Store user roles in session or persistent storage
    user_roles = ["Guest"]

    guest_menu_builder = MenuBuilder(main_menu_items, allowed_roles=user_roles)
    guest_menu_data = guest_menu_builder.generate_menu(user_roles=user_roles, is_authenticated=True, include_protected=False)

    # Print or use the guest_menu_data as needed
    print("Generated Menu for Guest after Login:", guest_menu_data)

    # Example usage for Logout
    # Clear or reset user roles from session or persistent storage
    user_roles = ["Guest"]

    # Example usage for Guest role after Logout
    guest_menu_builder = MenuBuilder(main_menu_items, allowed_roles=user_roles)
    guest_menu_data_after_logout = guest_menu_builder.generate_menu(user_roles=user_roles, is_authenticated=False, include_protected=False)

    # Print or use the guest_menu_data_after_logout as needed
    print("Generated Menu for Guest after Logout:", guest_menu_data_after_logout)

    #left menu test
    # Load menu items from JSON file
    json_file_path = get_current_directory() + '/static/js/left_menu_structure.json'
    with open(Path(json_file_path), 'r') as file:
        main_menu_items = json.load(file)

    # Example usage for Guest role during login
    # Store user roles in session or persistent storage
    user_roles = ["Employee"]

    guest_menu_builder = MenuBuilder(main_menu_items, allowed_roles=user_roles)
    guest_menu_data = guest_menu_builder.generate_menu(user_roles=user_roles, is_authenticated=True,
                                                       include_protected=False)
