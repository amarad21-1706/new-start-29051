from app_factory import create_app
from db import db
from models.user import TextContent

app = create_app()

with app.app_context():
    # Fetch all records from the text_content table
    records = TextContent.query.all()
    for record in records:
        # Replace <h2> with <h3> and </h2> with </h3> in content_body
        record.content_body = record.content_body.replace('<h2>', '<h3>').replace('</h2>', '</h3>')

    # Commit the changes to the database
    db.session.commit()
    print("All <h2> tags replaced with <h3> in content_body.")
