
from datetime import datetime, timedelta
from app.models.user import (CompanyUsers)

def validate_and_prepare_data(**kwargs):
    # Validate and prepare the data
    validated_data = {}

    # Validate and populate dates
    current_datetime = datetime.now()

    deadline_type = kwargs.get('deadline_type', 1)
    validated_data['interval_id'] = kwargs.get('deadline_type', 1)

    if deadline_type == 1:  # End of current year
        deadline = datetime(current_datetime.year, 12, 31, 23, 59, 59)
    elif deadline_type == 2:  # Semester
        if current_datetime.month <= 6:
            deadline = datetime(current_datetime.year, 6, 30, 23, 59, 59)
        else:
            deadline = datetime(current_datetime.year, 12, 31, 23, 59, 59)
    elif deadline_type == 3:  # 4-month period
        current_month = current_datetime.month
        if current_month <= 4:
            deadline = datetime(current_datetime.year, 4, 30, 23, 59, 59)
        elif current_month <= 8:
            deadline = datetime(current_datetime.year, 8, 31, 23, 59, 59)
        else:
            deadline = datetime(current_datetime.year, 12, 31, 23, 59, 59)
    elif deadline_type == 4:  # Quarter
        quarter_month = ((current_datetime.month - 1) // 3) * 3 + 1
        deadline = datetime(current_datetime.year, quarter_month + 2, 31, 23, 59, 59)
    elif deadline_type == 5:  # Month
        deadline = datetime(current_datetime.year, current_datetime.month, 31, 23, 59, 59)
    elif deadline_type == 6:  # Week
        deadline = current_datetime + timedelta(days=(6 - current_datetime.weekday()))

    validated_data['created_on'] = current_datetime
    validated_data['updated_on'] = current_datetime
    validated_data['deadline'] = deadline

    validated_data['status_id'] = 1
    validated_data['area_id'] = kwargs.get('current_area_id', 0)
    validated_data['subarea_id'] = kwargs.get('current_subarea_id', '0')
    validated_data['record_type'] = kwargs.get('current_record_type', 'area controllo')
    validated_data['data_type'] = kwargs.get('current_data_type', 'struttura offerta')
    validated_data['interval_id'] = kwargs.get('current_interval_id', 1)
    validated_data['status_id'] = kwargs.get('current_status_id', 1)

    # Populate user_id and status_id
    validated_data['user_id'] = kwargs.get('current_user_id', 0)
    print('validated user id', kwargs.get('current_user_id', 0))
    # Populate company_id (assuming it's retrieved from the current user's association)
    # You need to replace this with your actual logic to get the company_id from the association model
    # validated_data['company_id'] = get_company_id(kwargs.get('current_user_id'))  # Implement this function
    validated_data['company_id'] = CompanyUsers.query.filter_by(user_id=kwargs.get('current_user_id')).first().company_id

    return validated_data
