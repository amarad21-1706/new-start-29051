# blueprint_global.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from db import db  # Assuming you have a SQLAlchemy database instance
from models.user import (User, UserRoles, Role, Table, Questionnaire, Question, Answer, Company,
                         QuestionnaireCompanies, CompanyUsers)

blueprint_global = Blueprint('blueprint_global', __name__)

def retrieve_all_data(model):
    return model.query.all()

def apply_filters_old(model, **filters):
    query = model.query

    for column_name, value in filters.items():
        if value:
            column = getattr(model, column_name, None)
            if column is not None:
                query = query.filter(column.ilike(f"%{value}%"))

    return query.all()

# Assuming Basedata has a column named 'id'
def filter_basedata_by_id(query, id):
    if id is not None:
        return query.filter(Basedata.id == id)
    return query

def apply_filters(model, **filters):
    query = model.query

    for column_name, value in filters.items():
        if column_name == 'id':
            query = filter_basedata_by_id(query, value)
        elif value:
            column = getattr(model, column_name, None)
            if column is not None:
                query = query.filter(column.ilike(f"%{value}%"))

    return query.all()


@blueprint_global.route('/edit_data/<int:id>', methods=['GET', 'POST'])
def edit_data(id):
    model = User
    item = model.query.get_or_404(id)

    if request.method == 'GET':
        # Logic for rendering the edit form
        return render_template('edit_data.html', data=item)

    elif request.method == 'POST':
        # Logic for handling form submission and updating the data
        for column in model.__table__.columns:
            column_name = column.name
            # Exclude 'registration_date' from the update
            if column_name != 'registration_date' and column_name != 'email' and column_name != 'password' and column_name in request.form:
                setattr(item, column_name, request.form[column_name])

        db.session.commit()
        flash('Data updated successfully!', 'success')
        return redirect(url_for('blueprint_global.generic'))

    else:
        # Handle other HTTP methods if necessary
        abort(405)  # Method Not Allowed



@blueprint_global.route('/delete_data/<int:id>', methods=['GET', 'POST'])
def delete_data(id):
    # Your code to handle editing the question
    return render_template('delete_data.html', user_id=id)



# Add more functions as needed


@blueprint_global.route('/flussi_precomp_property/<int:id>/<int:lexic_id>', methods=['GET'])
def get_flussi_precomp_property(id, lexic_id):
    # Fetch Basedata instances, e.g., using your generic CRUD functions
    basedata_instance = get_basedata_instance_somehow(id)  # Replace with your actual method

    if basedata_instance is not None:
        # Apply the flussi_precomp_property logic to the instance
        flussi_precomp_property_result = basedata_instance.flussi_precomp_property(lexic_id)
        if flussi_precomp_property_result is not None:
            return jsonify(flussi_precomp_property_result)

    # Return an error response if the instance is not found or the flussi_precomp property is not applicable
    return jsonify({'error': 'Invalid ID or <flussi_precomp> property not applicable'}), 404



@blueprint_global.route('/generic')
def generic():
    # Retrieve filter parameters from the request object
    username_filter = request.args.get('username', '')
    firstname_filter = request.args.get('first_name', '')
    lastname_filter = request.args.get('last_name', '')

    # Apply filters to your data source (modify as needed)
    filtered_data = apply_filters(User, username=username_filter, firstname_filter=firstname_filter,
                                  lastname_filter=lastname_filter)

    # Render the filtered data
    return render_template('generic.html', data=filtered_data)



# flussi pre-complaint ad-hoc route
# alternatively, the generic route can be used, as per the following:
# blueprint_global.py

'''@blueprint_global.route('/generic_flussi_precomplaint')
def generic_flussi_precomplaint():
    # Retrieve filter parameters from the request object
    username_filter = request.args.get('username', '')
    firstname_filter = request.args.get('first_name', '')
    lastname_filter = request.args.get('last_name', '')

    # Apply filters to your data source (modify as needed)
    filtered_data = apply_filters(User, username=username_filter, firstname_filter=firstname_filter,
                                  lastname_filter=lastname_filter)

    # Get custom_property_value for the first Basedata instance (modify as needed)
    first_basedata_instance = get_basedata_instance_somehow(1)
    custom_property_value = get_custom_property(first_basedata_instance.lexic_id)

    # Render the generic CRUD template along with the custom property value
    return render_template('crud_read_template.html', data=filtered_data, custom_property=custom_property_value)'''


@blueprint_global.route('/flussi_precomplaint2')
def flussi_precomplaint2():
    # Your view logic goes here
    if "area_1" in request.url:
        print('build area 1 left menu')

    # Render the generic CRUD template
    return render_template('crud_read_template.html')
