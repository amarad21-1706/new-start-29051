
import json
from pathlib import Path

class MenuBuilder:
    def __init__(self, json_file_path='menuStructure101.json'):
        # Use Path to create a Path object
        with open(Path(json_file_path), 'r') as file:
            self.menu_data = json.load(file)
        self.Undefined = object()

    def parse_menu_data(self, menu_data):
        # Create an empty list to store the processed menu items
        menu_items = []

        for menu_item_name, menu_item_data in menu_data.items():
            print('*** menu_item_name', menu_item_data)
            if not isinstance(menu_item_data, dict):
                continue

            # Extract the submenus data
            label = menu_item_data.get('label', '')
            url = menu_item_data.get('url', '')
            protected = menu_item_data.get('protected', False)
            submenus = menu_item_data.get('submenus', {})

            # Update the menu items list
            menu_items.append({
                'label': label,
                'url': url,
                'protected': protected,
                'submenus': self.parse_menu_data(submenus) if submenus else []
            })

        return menu_items

    def processed_menu_data(self, menu_items):
        # Create a list to store the processed menu items
        processed_menu_items = []

        # Iterate through the menu items
        for menu_item_data in menu_items:
            if not isinstance(menu_item_data, dict):
                continue

            # Process the menu item
            if callable(self.process_menu):
                processed_menu_item = self.process_menu(menu_item_data)
            else:
                processed_menu_item = menu_item_data

            # Add the processed menu item to the list
            processed_menu_items.append(processed_menu_item)

        return processed_menu_items

    # ...

    def update_submenus(self, menu_tree, submenus):
        for submenu_label, submenu_data in submenus.items():
            if submenu_label not in menu_tree:
                menu_tree[submenu_label] = {
                    'label': submenu_label,
                    'url': submenu_data['url'],
                    'protected': submenu_data['protected'],
                    'submenus': {}

                }
            else:
                menu_tree[submenu_label]['submenus'].update(submenu_data)

            print('Added submenus for:', submenu_label)
            print(menu_tree)

        return menu_tree

    def process_menu(self, menu_item):
        if menu_item is self.Undefined:
            # Replace 'Undefined' with a valid data type
            menu_item = {}

        # Check if the menu item is JSON-serializable
        if not isinstance(menu_item, (dict, list, str)):
            raise TypeError(
                f"Object of type {type(menu_item).__name__} is not JSON serializable")

        # Process the submenus recursively
        if isinstance(menu_item.get('submenus'), list):
            processed_submenus = []
            for submenu_data in menu_item['submenus']:
                processed_submenu = self.processed_menu_data([submenu_data])
                processed_submenus.append(processed_submenu[0])
            menu_item['submenus'] = processed_submenus

        # Exclude 'protected' attribute from serialization
        menu_item.pop('protected', None)

        return menu_item

    # ...


# Example usage for self-testing
if __name__ == '__main__':
    def processed_menu_data(self, menu_data):
        # Create a dictionary to store the processed menu tree
        processed_menu_tree = {}

        # Iterate through the menu items
        for menu_item_name, menu_item_data in menu_data.items():
            if not isinstance(menu_item_data, dict):
                continue

            # Process the menu item
            if callable(self.process_menu):
                processed_menu_item = self.process_menu(menu_item_data)
            else:
                processed_menu_item = menu_item_data

            # Add the processed menu item to the processed menu tree
            processed_menu_tree[menu_item_name] = processed_menu_item

        return processed_menu_tree


    # ...

# Example usage for self-testing
if __name__ == '__main__':
    menu_builder = MenuBuilder()
    authenticated_user_menu = menu_builder.parse_menu_data(menu_builder.menu_data)
    print(json.dumps(authenticated_user_menu, indent=2))


