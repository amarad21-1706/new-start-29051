import json

class MenuBuilder:
    def __init__(self, json_file_path='menuStructure101.json'):
        with open(json_file_path, 'r') as file:
            self.menu_data = json.load(file)

    def get_menu_items(self, section=None):
        processed_menus = {}
        main_menu_items = []

        if section is None:
            sections = self.menu_data.keys()
        else:
            sections = [section]

        print(f"Available keys: {list(self.menu_data.keys())}")  # Add this line for debugging

        for section in sections:
            print(f"Processing section: {section}")
            print(section in processed_menus)
            if section not in processed_menus:
                print('so get going', section)
                menu_item = self._get_menu_item(section, processed_menus)
                main_menu_items.append(menu_item)

        return main_menu_items

    def _get_menu_item(self, section, processed_menus):
        processed_menus[section] = True
        submenu_data = self.menu_data[section]

        label = submenu_data.get('label', '')
        url = submenu_data.get('url', '')
        submenus_data = submenu_data.get('submenus', {})

        submenus = []
        for submenu_label, submenu_url in submenus_data.items():
            if submenu_label not in processed_menus:
                submenus.append({'label': submenu_label, 'url': submenu_url})
                processed_menus[submenu_label] = True

        return {'label': label, 'url': url, 'submenus': submenus}


if __name__ == '__main__':
    app = MenuBuilder()
    main_menu_items = app.get_menu_items(section='Home')
    print(main_menu_items)
