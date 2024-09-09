# app/menu_builder.py
from pathlib import Path
import json
from utils.utils import get_current_directory
from jinja2.runtime import Undefined
from config.config import generate_statistics_menu


class MenuBuilder:
    def __init__(self, menu_data, allowed_roles=None):
        self.menu_data = menu_data
        self.allowed_roles = allowed_roles or []

    def generate_menu(self, user_roles=None, is_authenticated=False):
        # If user is authenticated but has no roles, assume 'Guest'
        if is_authenticated and not user_roles:
            user_roles = ['Guest']

        # Generate the menu items based on the user's roles and authentication status
        menu_items = self.parse_menu_data(user_roles=user_roles, is_authenticated=is_authenticated)
        print("Generated menu successfully")
        return menu_items


    def parse_menu_data(self, user_roles=None, is_authenticated=False, raw_menu_data=None, depth=0):
        if depth > 10:  # Adjust this depth limit as needed
            print(f"Maximum recursion depth reached: {depth}")
            return []

        if raw_menu_data is None:
            raw_menu_data = self.menu_data

        menu_items = []

        if isinstance(raw_menu_data, dict):
            for menu_item_name, menu_item_data in raw_menu_data.items():
                if not isinstance(menu_item_data, dict):
                    continue

                label = menu_item_data.get('label')
                url = menu_item_data.get('url')
                protected = menu_item_data.get('protected', False)
                allowed_roles = menu_item_data.get('allowed_roles', [])

                print(f"Processing menu item: {label}, URL: {url}, Protected: {protected}, Allowed Roles: {allowed_roles}, User Roles: {user_roles}, Is Authenticated: {is_authenticated}")

                # Skip menu items without proper attributes
                if any(value is None for value in (label, url)):
                    print(f"Skipping menu item due to missing attributes: {label}, {url}")
                    continue

                # Check if the user has any of the required roles to access this menu item
                if not any(role in allowed_roles for role in user_roles):
                    print(f"Skipping item due to missing required roles: {label}")
                    continue

                # Recursively parse submenus
                submenus = menu_item_data.get('submenus', {})

                if label == "Statistics":
                    dynamic_statistics_submenus = generate_statistics_menu()
                    submenus.update(dynamic_statistics_submenus)

                try:
                    print("Before parsing submenus...")
                    # Rest of your function as before, with the addition of `depth + 1` in recursive call
                    parsed_submenus = self.parse_menu_data(
                        user_roles=user_roles,
                        is_authenticated=is_authenticated,
                        raw_menu_data=submenus,
                        depth=depth + 1
                    )
                    print("After parsing submenus...")
                except Exception as e:
                    print(f"Error occurred while parsing submenus: {e}")
                    raise

                if parsed_submenus or not submenus:
                    menu_items.append({
                        'label': label,
                        'url': url,
                        'protected': protected,
                        'allowed_roles': allowed_roles,
                        'user_roles': user_roles,
                        'submenus': parsed_submenus
                    })

            print("Completed parsing all menu items")
            return menu_items
        else:
            print("Raw menu data is not a dictionary")
            return []


def load_menu_items(json_file_path):
    """Load menu items from a given JSON file."""
    with open(Path(json_file_path), 'r') as file:
        return json.load(file)

def generate_menu_for_role(main_menu_items, user_roles, is_authenticated):
    """Generate menu for a given role and authentication state."""
    menu_builder = MenuBuilder(main_menu_items, allowed_roles=user_roles)
    return menu_builder.generate_menu(user_roles=user_roles, is_authenticated=is_authenticated)


if __name__ == '__main__':
    print("Start")

    # Load main menu items for different scenarios
    main_menu_items = load_menu_items(get_current_directory() + '/static/js/menuStructure101.json')
    left_menu_items = load_menu_items(get_current_directory() + '/static/js/left_menu_structure.json')

    # Example usage for Guest role during login
    guest_menu_data_login = generate_menu_for_role(main_menu_items, ["Guest"], is_authenticated=True)
    print("Generated Menu for Guest after Login:", guest_menu_data_login)

    # Example usage for Guest role after Logout
    guest_menu_data_logout = generate_menu_for_role(main_menu_items, ["Guest"], is_authenticated=False)
    print("Generated Menu for Guest after Logout:", guest_menu_data_logout)

    # Example usage for Left Menu for Employee role
    left_menu_data_employee = generate_menu_for_role(left_menu_items, ["Employee"], is_authenticated=True)
    print("Generated Left Menu (left_menu_data) is:", left_menu_data_employee)
