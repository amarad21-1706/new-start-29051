from models.user import Lexic, LexicSubcategory, LexicItem
from db import db
from app import create_app

# Create the Flask app instance
app = create_app()


with app.app_context():
    lexic_id = 7  # Replace with the actual ID

    # Get all subcategories for the lexic
    subcategories = LexicSubcategory.query.filter_by(parent_id=lexic_id).all()

    for subcategory in subcategories:
        # Delete all items in the subcategory
        LexicItem.query.filter_by(subcategory_id=subcategory.id).delete()

    # Delete the subcategories
    LexicSubcategory.query.filter_by(parent_id=lexic_id).delete()

    # Finally, delete the lexic record
    Lexic.query.filter_by(id=lexic_id).delete()

    db.session.commit()
    print(f"Deleted lexic ID {lexic_id}, its subcategories, and related items.")