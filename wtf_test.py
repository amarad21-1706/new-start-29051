from flask import Flask, render_template_string, request
from wtforms import Form, StringField, validators, ValidationError

# Define the Flask application
app = Flask(__name__)

# Define a custom validator
def custom_email_validator(form, field):
    if "@example.com" not in field.data:
        raise ValidationError("Must be an example.com email address")

# Define a WTForms Form
class ExampleForm(Form):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(),
        custom_email_validator  # Add the custom validator
    ])

# Define the route with a form
@app.route('/', methods=['GET', 'POST'])
def home():
    form = ExampleForm(request.form)
    if request.method == 'POST' and form.validate():
        return 'Form Successfully Submitted!'
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simple Form</title>
        </head>
        <body>
            <form method="post" action="/">
                Email: <input type="text" name="email" value="{{ form.email.data }}"/>
                {% for error in form.email.errors %}
                    <div style="color: red;">{{ error }}</div>
                {% endfor %}
                <input type="submit" value="Submit" />
            </form>
        </body>
        </html>
    ''', form=form)

if __name__ == '__main__':
    app.run(debug=True)
