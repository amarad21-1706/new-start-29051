from app import create_app
from db import db
from models.user import Lexic, LexicSubcategory, LexicItem  # Adjust imports as needed

# Create the Flask app instance
app = create_app()

with app.app_context():
    # Step 1: Create the top-level category
    category_name = "Oggetti ricorrenti contenziosi"
    category = Lexic.query.filter_by(name=category_name).first()
    if not category:
        category = Lexic(category="Contenziosi", name=category_name)
        db.session.add(category)
        db.session.commit()

    # Step 2: Define subcategories and items
    subcategories_data = [
        {
            "name": "Atti di impulso del procedimento",
            "items": [
                "Citazione",
                "Ricorso amministrativo",
                "Altro",
            ],
        },
        {
            "name": "Atti prodotti nell'ambito del procedimento giurisdizionale",
            "items": [
                "Memorie",
                "Decreti",
                "Decisioni",
                "Altro",
            ],
        },
        {
            "name": "Atti della procedura arbitrale",
            "items": [
                "Atti della procedura arbitrale",
                "Altro",
            ],
        },
        {
            "name": "Atti della procedura di conciliazione",
            "items": [
                "Atti della procedura di conciliazione",
                "Altro",
            ],
        },
    ]

    # Step 3: Insert subcategories and items
    for subcategory_data in subcategories_data:
        subcategory_name = subcategory_data["name"]
        items = subcategory_data["items"]

        # Check if the subcategory already exists
        subcategory = LexicSubcategory.query.filter_by(name=subcategory_name, parent_id=category.id).first()
        if not subcategory:
            subcategory = LexicSubcategory(parent_id=category.id, name=subcategory_name)
            db.session.add(subcategory)

        # Insert items for the subcategory
        for item_name in items:
            item = LexicItem.query.filter_by(name=item_name, subcategory_id=subcategory.id).first()
            if not item:
                item = LexicItem(subcategory_id=subcategory.id, name=item_name)
                db.session.add(item)

    # Commit all the changes
    db.session.commit()
    print("Subcategories and items have been added successfully.")
