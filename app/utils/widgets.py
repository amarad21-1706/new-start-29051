from flask_admin.form import RenderTemplateWidget

class XEditableWidget(RenderTemplateWidget):
    def __init__(self):
        super(XEditableWidget, self).__init__('xeditable_widget.html')

from wtforms import FileField

class FileUploadField(FileField):
    def __init__(self, label=None, validators=None, base_path=None, **kwargs):
        super(FileUploadField, self).__init__(label, validators, **kwargs)
        self.base_path = base_path
