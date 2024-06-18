
from datetime import datetime, timedelta

from flask import render_template
from app_factory import create_app

from models.user import BaseData, StepBaseData
# from card_generator import get_records_count_for_area, get_records_filled_by_area, get_documents_due_last_three_days,
# get_documents_overdue, get_documents_completed

app = create_app()

# Assuming you have a function to get the current user's role
def get_user_role():
    # Logic to get the current user's role
    pass

@app.route('/home')
def home():
    user_role = get_user_role()

    # Generate cards based on the user's role
    cards_data = []

    if user_role == 'admin':
        # Generate cards for admin
        cards_data.append({'title': 'Records Found for Area 1', 'content': get_records_count_for_area('Area 1')})
        cards_data.append({'title': 'Records Found for Area 2', 'content': get_records_count_for_area('Area 2')})
        cards_data.append({'title': 'Records Found for Area 3', 'content': get_records_count_for_area('Area 3')})
        cards_data.append({'title': 'Documents Due in Last Three Days', 'content': get_documents_due_last_three_days()})
        cards_data.append({'title': 'Documents Overdue', 'content': get_documents_overdue()})
        cards_data.append({'title': 'Documents Completed', 'content': get_documents_completed()})
    elif user_role == 'authority':
        # Generate cards for authority
        cards_data.append({'title': 'Records Filled for Area 1', 'content': get_records_filled_by_area('Area 1')})
        cards_data.append({'title': 'Records Filled for Area 2', 'content': get_records_filled_by_area('Area 2')})
        cards_data.append({'title': 'Records Filled for Area 3', 'content': get_records_filled_by_area('Area 3')})
    elif user_role == 'manager':
        # Generate cards for manager
        cards_data.append({'title': 'Documents Due in Last Three Days', 'content': get_documents_due_last_three_days()})
        cards_data.append({'title': 'Documents Overdue', 'content': get_documents_overdue()})
    elif user_role == 'employee':
        # Generate cards for employee
        cards_data.append({'title': 'Documents Due in Last Three Days', 'content': get_documents_due_last_three_days()})
    elif user_role == 'guest':
        # Generate cards for guest
        cards_data.append({'title': 'Records Found for Area 1', 'content': get_records_count_for_area('Area 1')})

    return render_template('home.html', cards_data=cards_data)


def get_records_count_for_area(area):
    # Query the database to get the count of records for a specific area
    # Assuming you have a method to query the records for each area
    return BaseData.query.filter_by(area=area).count()

def get_records_filled_by_area(area):
    # Query the database to get the count of filled records for a specific area
    # Assuming you have a method to query filled records for each area
    return BaseData.query.filter_by(area=area, is_filled=True).count()

def get_documents_due_last_three_days():
    today = datetime.now().date()
    three_days_ago = today - timedelta(days=3)
    # Query the database to get documents due in the last three days
    # Assuming deadline_date is a column in StepBaseData table
    return StepBaseData.query.filter(StepBaseData.deadline_date <= today,
                                     StepBaseData.deadline_date >= three_days_ago,
                                     StepBaseData.base_data.has(BaseData.file_path.isnot(None))).count()

def get_documents_overdue():
    today = datetime.now().date()
    # Query the database to get documents overdue
    # Assuming deadline_date is a column in StepBaseData table
    return StepBaseData.query.filter(StepBaseData.deadline_date < today,
                                     StepBaseData.base_data.has(BaseData.file_path.isnot(None))).count()

def get_documents_completed():
    # Query the database to get documents completed
    # Assuming is_completed is a column in StepBaseData table
    return StepBaseData.query.filter(StepBaseData.is_completed == True, StepBaseData.base_data.has(BaseData.file_path.isnot(None))).count()



