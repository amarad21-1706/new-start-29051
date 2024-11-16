from app_factory import create_app
from db import db
from models.user import TextContent

# Create the Flask app
app = create_app()

# Use the app context
with app.app_context():
    # Define the content
    content_body = """
    <h1>La nostra missione</h1>
    <hr>
    <p>Questo è il motivo per cui siamo qui.</p>
    <p>Self-audit.</p>
    <p>Conformità.</p>
    <hr>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam hendrerit nisi sed sollicitudin pellentesque. Nunc posuere purus rhoncus pulvinar aliquam. Ut aliquet tristique nisl vitae volutpat. Nulla aliquet porttitor venenatis. Donec a dui et dui fringilla consectetur id nec massa. Aliquam erat volutpat. Sed ut dui ut lacus dictum fermentum vel tincidunt neque. Sed sed lacinia lectus. Duis sit amet sodales felis. Duis nunc eros, mattis at dui ac, convallis semper risus. In adipiscing ultrices tellus, in suscipit massa vehicula eu.</p>
    """

    # Create the record

    # Create the record
    new_content = TextContent(
        content_type='mission',
        content_body=content_body,
        language_code='it',
        title='La nostra missione'
    )

    # Add and commit to the database
    with app.app_context():
        db.session.add(new_content)
        db.session.commit()

    print("TextContent record for 'missione' in Italian created successfully!")
