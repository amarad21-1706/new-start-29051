from flask_admin.form.upload import FileUploadField

class CustomFileUploadField(FileUploadField):
    def __init__(self, label=None, validators=None, base_path=None, **kwargs):
        super().__init__(label=label, validators=validators, base_path=base_path, **kwargs)

