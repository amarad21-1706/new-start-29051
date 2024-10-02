# blueprints_data.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from .models import Data  # Assuming you have a Data model

data_bp = Blueprint('data', __name__)

# Replace this with your actual data source logic or API calls
def retrieve_all_data_from_data_source():
    return Data.query.all()

def apply_filters(text_filter, answer_type_filter):
    # Replace this with your actual filtering logic
    # For example, if using SQLAlchemy and you have a Data model:
    query = Data.query

    if text_filter:
        query = query.filter(Data.text.ilike(f"%{text_filter}%"))

    if answer_type_filter:
        query = query.filter(Data.answer_type.ilike(f"%{answer_type_filter}%"))

    return query.all()

@data_bp.route('/data')
def data():
    # Retrieve filter parameters from the request object
    text_filter = request.args.get('text', '')
    answer_type_filter = request.args.get('answer_type', '')

    # Check if filters are provided
    if text_filter or answer_type_filter:
        print('filter')
        # Apply filters to your data source
        filtered_data = apply_filters(text_filter, answer_type_filter)
    else:
        print('no filter')
        # If no filters are provided, retrieve all data
        filtered_data = retrieve_all_data_from_data_source()

    # Print debug information
    print("Filtered Data:", filtered_data)
    print("Number of Data:", len(filtered_data))

    # Render the filtered data
    return render_template('data.html', data=filtered_data)

@data_bp.route('/edit_data/<int:id>', methods=['GET', 'POST'])
def edit_data(id):
    if request.method == 'GET':
        # Logic for rendering the edit form
        data_item = Data.query.get_or_404(id)
        return render_template('edit_data.html', data_item=data_item)

    elif request.method == 'POST':
        # Logic for handling form submission and updating the data
        data_item = Data.query.get_or_404(id)
        data_item.text = request.form['text']
        data_item.answer_type = request.form['answer_type']
        # Add other form fields as needed
        db.session.commit()
        flash('Data updated successfully!', 'success')
        return redirect(url_for('data.data'))

    else:
        # Handle other HTTP methods if necessary
        abort(405)  # Method Not Allowed

@data_bp.route('/delete_data/<int:id>')
def delete_data(id):
    # Your code to handle deleting the data
    return render_template('delete_data.html', data_id=id)
