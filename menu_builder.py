# app/menu_builder.py
from pathlib import Path
import json
from utils.utils import get_current_directory
from jinja2.runtime import Undefined
from config.config import generate_statistics_menu
from flask import g, current_app


class MenuBuilder:
    def __init__(self, menu_data, allowed_roles=None):
        self.menu_data = menu_data
        self.allowed_roles = allowed_roles or ['Guest']

    def generate_menu(self, user_roles=None, is_authenticated=False, include_protected=False):
        # If the user is not authenticated, assume "Guest" role
        if not is_authenticated:
            user_roles = user_roles or ['Guest']

        print('Rappel is auth: maybe I should use g. here?', is_authenticated, g.user.is_authenticated)
        # Generate the menu items based on the user's roles and authentication status
        menu_items = self.parse_menu_data(user_roles=user_roles, is_authenticated=is_authenticated, include_protected=include_protected)
        return menu_items

    def parse_menu_data(self, user_roles=None, is_authenticated=False, include_protected=False, raw_menu_data=None):
        if raw_menu_data is None:
            raw_menu_data = self.menu_data

        menu_items = []

        user_roles = user_roles or ['Guest']

        if isinstance(raw_menu_data, dict):
            for menu_item_name, menu_item_data in raw_menu_data.items():
                if not isinstance(menu_item_data, dict):
                    continue

                label = menu_item_data.get('label')
                url = menu_item_data.get('url')
                protected = menu_item_data.get('protected', False)
                allowed_roles = menu_item_data.get('allowed_roles', [])

                # Debugging output to trace the values
                print(f"Processing menu item: {label}, URL: {url}, Protected: {protected}, Allowed Roles: {allowed_roles}, User Roles: {user_roles}, Is Authenticated: {is_authenticated}")

                # Skip menu items without proper attributes
                if any(value is None for value in (label, url)):
                    print(f"Skipping menu item due to missing attributes: {label}, {url}")
                    continue

                # Skip protected menu items if user is not authenticated and the item is protected
                if protected and not is_authenticated:
                    print(f"Skipping protected item as user is not authenticated: {label}")
                    continue

                # Check if the authenticated user has the required role to access the menu item
                if user_roles and not any(role in allowed_roles for role in user_roles):
                    print(f"Skipping item due to missing required roles: {label}")
                    continue

                # Recursively parse submenus
                submenus = menu_item_data.get('submenus', {})

                if label == "Statistics":
                    dynamic_statistics_submenus = generate_statistics_menu()
                    submenus.update(dynamic_statistics_submenus)

                parsed_submenus = self.parse_menu_data(
                    user_roles=user_roles,
                    is_authenticated=is_authenticated,
                    include_protected=include_protected,
                    raw_menu_data=submenus
                )

                # Only add the menu item if it has allowed submenus or itself is allowed
                if parsed_submenus or not submenus:
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
                parsed_submenus = self.parse_menu_data(
                    user_roles=user_roles,
                    is_authenticated=is_authenticated,
                    include_protected=include_protected,
                    raw_menu_data=menu_item_data.get('submenus', {})
                )

                menu_items.append({
                    'label': menu_item_data.get('label'),
                    'url': menu_item_data.get('url'),
                    'protected': menu_item_data.get('protected', False),
                    'allowed_roles': menu_item_data.get('allowed_roles', []),
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

    # Print or use the guest_menu_data as needed
    print("Generated Left Menu (left_menu_data) is:", guest_menu_data)
