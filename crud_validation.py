from sqlalchemy import inspect
from utils.utils import get_except_fields
from flask import jsonify

# validate each field
def validate_and_add_item(model, request, db):
    inspector = inspect(model)
    mapped_table = inspector.mapper
    table_columns = mapped_table.columns
    except_fields = get_except_fields()  # Define your function to get excluded fields

    field_names = [field.name for field in table_columns if field.name not in except_fields]

    print('validation; method is', request.method, 'model is', model)

    if request.method == 'POST':
        new_item = model()

        print('validation; method is', request.method, 'new item', new_item)

        for key, value in request.form.items():
            if key in ['created_on', 'updated_on', 'end_of_registration']:
                if not value or value.lower() == 'none':
                    value = None
                else:
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        print(f"Invalid datetime format for {key}: {value}")
                        continue

            # Validate field type before setting the value
            if not validate_field_type(model, key, value):
                return jsonify({'status': 'error', 'message': f'Invalid data type for field {key}'})

            setattr(new_item, key, value)

        print('ready to commit data, vector is new_item')
        print(new_item)

        db.session.add(new_item)
        db.session.commit()
        # Return a JSON response indicating success
        return jsonify({'status': 'success', 'message': 'Item added successfully'})


def validate_field_type(model, field_name, value):
    # Get the column for the specified field
    column = getattr(model, field_name)

    # Perform validation based on the column type
    if column.type.python_type == int:
        return isinstance(value, int)
    elif column.type.python_type == str:
        return isinstance(value, str)
    elif column.type.python_type == datetime:
        # Check if the value can be converted to datetime
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    # Add more validation for other data types as needed

    # Default to True if the type is not handled
    return True

