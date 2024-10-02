
from flask import abort

def can_view_record(user, record):
    if user.role == 'admin':
        return True
    elif user.role == 'manager':
        return user.company == record.company
    elif user.role == 'user':
        return user.id == record.user_id
    return False


#@app.route('/view_record/<model_name>/<int:item_id>')
def view_record(model_name, item_id):
    model_class = get_model_by_name(model_name)
    item = model_class.query.get_or_404(item_id)

    if not can_view_item(current_user, item):
        abort(403)  # Forbidden

    # Render the view...
    # or else return item
    return item

def get_user_records(user, model):
    if user.role == 'admin':
        return model.query.all()
    elif user.role == 'manager':
        return model.query.filter_by(company=user.company).all()
    elif user.role == 'user':
        return model.query.filter_by(user_id=user.id).all()
    return []



