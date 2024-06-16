from flask import Flask, render_template_string, request
from flask_wtf import FlaskForm
from wtforms import StringField, validators, ValidationError
from wtforms.validators import DataRequired, Email

# Set up Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Required for CSRF protection in Flask-WTF

# Define a custom validator
def custom_email_validator(form, field):
    if "@example.com" not in field.data:
        raise ValidationError("Must be an example.com email address")

# Define a FlaskForm
class ExampleFlaskForm(FlaskForm):
    email = StringField('Email', [
        DataRequired(),
        Email(),
        custom_email_validator
    ])

# Define route with a form using FlaskForm
@app.route('/', methods=['GET', 'POST'])
def home():
    form = ExampleFlaskForm()
    if form.validate_on_submit():
        return 'Form Successfully Submitted!'
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simple Form</title>
        </head>
        <body>
            <form method="post" action="/" enctype="multipart/form-data">
                {{ form.hidden_tag() }}  <!-- For CSRF token -->
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
