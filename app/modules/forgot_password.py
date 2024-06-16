from flask import Flask, request, render_template, redirect, url_for, flash, session
from twilio.rest import Client
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load environment variables
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
authy_api_key = os.environ.get('TWILIO_AUTHY_API_KEY')

client = Client(account_sid, auth_token)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = get_user_by_email(email)  # Implement this function to fetch user by email

        if user:
            # Send a verification token via Twilio Authy
            authy_id = user.authy_id  # Store Authy ID with user information
            client.authy.services.create_verification(
                to=user.phone_number,
                channel='sms',
                via='sms',
                code_length=6,
                locale='en',
                custom_message='Your password reset code is: {code}'
            )

            session['email'] = email
            return redirect(url_for('verify_token'))

        flash('No user found with that email address', 'danger')

    return render_template('forgot_password.html')


@app.route('/verify_token', methods=['GET', 'POST'])
def verify_token():
    if request.method == 'POST':
        token = request.form['token']
        email = session.get('email')
        user = get_user_by_email(email)  # Implement this function to fetch user by email

        if user:
            # Verify the token using Twilio Authy
            verification = client.authy.services.verifications.check(
                to=user.phone_number,
                code=token
            )

            if verification.status == 'approved':
                return redirect(url_for('reset_password'))

        flash('Invalid token', 'danger')

    return render_template('verify_token.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        password = request.form['password']
        email = session.get('email')
        user = get_user_by_email(email)  # Implement this function to fetch user by email

        if user:
            user.set_password(password)  # Implement this function to set user's new password
            session.pop('email', None)
            flash('Password reset successfully', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html')


def get_user_by_email(email):
    # Implement this function to fetch user by email from the database
    pass


if __name__ == '__main__':
    app.run(debug=True)
