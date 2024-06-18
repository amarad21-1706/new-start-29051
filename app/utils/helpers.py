from flask import current_app
from app.utils.widgets import FileUploadField

def create_file_upload_field():
    with current_app.app_context():
        return FileUploadField('File', base_path=current_app.config['UPLOAD_FOLDER'])
