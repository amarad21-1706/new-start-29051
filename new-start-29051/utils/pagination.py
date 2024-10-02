
def paginate_data1(data_source, page, per_page, error_out):
    # Fetch paginated data from the data source

    print('PAGE IS', page)

    items = data_source.query(page, per_page)

    # Check if there are any items
    if items is None or len(items.items) == 0:
        if error_out:
            raise Exception('No data found')
        else:
            return None

    # Prepare the paginated data object
    return {
        'items': items.items,
        'page': items.page,
        'per_page': items.per_page,
        'total': items.total
    }

def paginate_data2(data_source, page, per_page, error_out):
    # Assuming data_source is an instance of CentralDataDataSource
    paginated_data = data_source.query(page, per_page)

    # Check if there are any items
    if paginated_data is None or len(paginated_data.items) == 0:
        if error_out:
            raise Exception('No data found')
        else:
            return None

    # Return the paginated result directly
    return paginated_data


def paginate_data(data_source, page, per_page, error_out):
    items = data_source.query(page, per_page)

    if items is None or len(items.items) == 0:
        if error_out:
            raise Exception('No data found')
        else:
            return None

    # Only return the items, not the entire pagination object
    return items.items
