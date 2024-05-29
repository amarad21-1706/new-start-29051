# workflow (example) - opening session - sending mails - sending follow up mails - closing session

from datetime import datetime, timedelta
from flask_mail import Message
from models.user import Workflow, Step, User
from app_factory import create_app
from db import db

appw = create_app()
db.init_app(appw)
print('one')

def open_document_gathering_session(workflow_id, deadline):
    with appw.app_context():
        # Get the workflow object
        print('two')
        workflow = Workflow.query.get(workflow_id)

        # Update the status of the workflow
        workflow.status = "Document Gathering Session Opened"
        db.session.commit()

        # Set the deadline in a file or database record
        # For demonstration, let's assume we are updating the workflow record itself
        workflow.deadline_date = deadline
        db.session.commit()

def send_email_to_users(workflow_id):
    with appw.app_context():
        # Get the workflow object
        workflow = Workflow.query.get(workflow_id)

        # Get the list of users associated with this workflow
        users = User.query.join(Workflow).filter(Workflow.id == workflow_id).all()

        # Compose and send email to each user
        for user in users:
            msg = Message(subject="Document Gathering Session",
                          recipients=[user.email],
                          body="Please submit your documents for the workflow: {}".format(workflow.name))
            mail.send(msg)

def send_follow_up_emails(workflow_id, deadline):
    # Get the workflow object
    with appw.app_context():
        workflow = Workflow.query.get(workflow_id)

        # Get the list of users associated with this workflow
        users = User.query.join(Workflow).filter(Workflow.id == workflow_id).all()

        # Calculate the time before the deadline for sending follow-up emails
        reminder_period = timedelta(days=7)  # Send reminder 7 days before the deadline
        reminder_date = deadline - reminder_period

        # Compose and send follow-up email to each user
        for user in users:
            msg = Message(subject="Reminder: Document Gathering Session Deadline",
                          recipients=[user.email],
                          body="Friendly reminder: The deadline for document submission is approaching for the workflow: {}. Please ensure all documents are submitted by {}".format(workflow.name, reminder_date))
            mail.send(msg)

def close_document_gathering_session(workflow_id):
    # Get the workflow object
    with appw.app_context():
        workflow = Workflow.query.get(workflow_id)

        # Update the status of the workflow
        workflow.status = "Document Gathering Session Closed"
        db.session.commit()


if __name__ == "__main__":
    print("Executing main block...")
    # Your main script logic here
    # Example usage:
    print('go')
    workflow_id = 1
    deadline_date = datetime.now() + timedelta(days=7)  # Assuming deadline is set to 30 days from now
    open_document_gathering_session(workflow_id, deadline_date)