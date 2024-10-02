# area_2.py
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user
from models.user import Table
from forms.forms import TableForm
from db import db
from config.config import Config
crt_directory = Config.CURRENT_DIR

area_2_bp = Blueprint('area_2', __name__, template_folder='templates')


@area_2_bp.route('/area_2', methods=['GET', 'POST'])
def area_2():
    user_id = current_user.id

    # Fetch existing data
    tables = Table.query.filter_by(user_id=user_id, name='Tabella 2').all()

    tables_data = []
    for table in tables:
        tables_data.append({
            'id': table.id,
            'name': table.name,
            'description': table.description,
            'user_id': current_user.id,
            'column1': table.column1,
            'column2': table.column2,
            'creation_date': table.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        })

    form = TableForm()

    if form.validate_on_submit():
        # Handle form submission for add, update, or remove
        action = form.action.data
        if action == 'add':
            # Add logic here
            new_table = Table(
                name=form.name.data,
                description=form.description.data,
                user_id=current_user.id,
                column1=form.column1.data,
                column2=form.column2.data
            )
            db.session.add(new_table)
        elif action == 'update':
            # Update logic here
            table_id = form.id.data
            table = Table.query.get(table_id)
            if table:
                table.name = form.name.data
                table.description = form.description.data
                table.column1 = form.column1.data
                table.column2 = form.column2.data
        elif action == 'remove':
            # Remove logic here
            table_id = form.id.data
            table = Table.query.get(table_id)
            if table:
                db.session.delete(table)

        # Commit changes
        db.session.commit()

        # Redirect to avoid form resubmission
        return redirect(url_for('area_2'))

    return render_template('workflow/control_areas/area_2.html', tables_data=tables_data, form=form)


@area_2_bp.route('/area_2_data', methods=['GET'])
def area_2_data():
    # Fetch and return the data as JSON
    user_id = current_user.id
    tables = Table.query.filter_by(user_id=user_id, name='Tabella 2').all()
    tables_data = []
    for table in tables:
        tables_data.append({
            'id': table.id,
            'name': table.name,
            'column1': table.column1,
            'column2': table.column2,
            'creation_date': table.creation_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(tables_data)

@area_2_bp.route(crt_directory + '/workflow/control_areas/area_2_update', methods=['POST'])
def area_2_update():
    data = request.get_json()
    temp_id = str(data.get('id'))  # Convert to string

    fields = data.get('fields')

    if temp_id and temp_id.startswith('temp_'):
        # This is a temporary row, add it to the database
        new_table = Table(
            name=fields.get('name'),
            description='',  # Adjust as needed
            user_id=current_user.id,
            column1=fields.get('column1'),
            column2=fields.get('column2')
        )
        db.session.add(new_table)
        db.session.commit()

        # Get the newly assigned ID from the database
        new_id = new_table.id

        # Return the new ID to the client
        return jsonify(success=True, new_id=new_id)
    else:
        # Update the existing row
        table_id = temp_id.lstrip('temp_')
        table = Table.query.get(table_id)
        if table:
            table.name = fields.get('name')
            table.column1 = fields.get('column1')
            table.column2 = fields.get('column2')
            db.session.commit()
            return jsonify(success=True)
        else:
            return jsonify(success=False, error='Table not found')

@area_2_bp.route('/workflow/control_areas/area_2_delete', methods=['POST'])
def area_2_delete():
    data = request.get_json()
    table_id = data['id']

    table = Table.query.get(table_id)
    if table:
        # Delete the table
        db.session.delete(table)
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, message='Table not found'), 404
