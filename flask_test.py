from app import create_app
from db import db
from models.user import Lexic, LexicSubcategory, LexicItem  # Adjust imports as needed

# Create the Flask app instance
app = create_app()

with app.app_context():
    # Step 1: Create the top-level category
    category_name = "Oggetti ricorrenti pre-complaint"
    category = Lexic.query.filter_by(name=category_name).first()
    if not category:
        category = Lexic(category="Pre-complaint", name=category_name)
        db.session.add(category)
        db.session.commit()

    # Step 2: Define subcategories and items
    subcategories_data = [
        {
            "name": "Da Utente su erogazione del servizio di distribuzione",
            "items": [
                "Esiti procedure di settlement fisico",
                "Gestione procedure di switching",
                "Bonus sociale",
                "Gestione partite commerciali contratto di distribuzione",
                "Altro",
            ],
        },
        {
            "name": "Da Utente su questioni di interesse del proprio cliente finale",
            "items": [
                "Switching – doppia fatturazione",
                "Misura",
                "Fatturazione",
                "Bonus sociale",
                "Mercato",
                "Morosità e sospensione del servizio",
                "Allacciamento",
                "Interventi su impianto",
                "Qualità commerciale",
                "Altro",
            ],
        },
        {
            "name": "Da cliente finale su questioni relative al contratto di vendita o al contratto di settlement fisico",
            "items": [
                "Switching – doppia fatturazione",
                "Misura",
                "Fatturazione",
                "Bonus sociale",
                "Mercato",
                "Morosità e sospensione del servizio",
                "Allacciamento",
                "Interventi su impianto",
                "Qualità commerciale",
                "Altro",
            ],
        },
        {
            "name": "Da cliente finale tramite sportello del consumatore",
            "items": [
                "Switching – doppia fatturazione",
                "Misura",
                "Fatturazione",
                "Bonus sociale",
                "Mercato",
                "Morosità e sospensione del servizio",
                "Allacciamento",
                "Interventi su impianto",
                "Qualità commerciale",
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
            db.session.commit()

        # Insert items for the subcategory
        for item_name in items:
            item = LexicItem.query.filter_by(name=item_name, subcategory_id=subcategory.id).first()
            if not item:
                item = LexicItem(subcategory_id=subcategory.id, name=item_name)
                db.session.add(item)

    # Commit all the changes
    db.session.commit()
    print("Subcategories and items have been added successfully.")
