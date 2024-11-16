from db import db
from models.user import TextContent
from app_factory import create_app

# Create the Flask app
app = create_app()

# Use the app context
with app.app_context():
    # Define the content
    content_body = """
    <h1>Termini di Utilizzo</h1>
    <p>Ultimo aggiornamento: {{ last_updated }}</p>
    
    <h2>1. Introduzione</h2>
    <p>Benvenuto su {{ app_name }}. Questi Termini di Utilizzo regolano l'uso del nostro sito web situato a {{ website_url }} e costituiscono un accordo contrattuale vincolante tra te e noi.</p>
    
    <h2>2. Accettazione dei Termini</h2>
    <p>Accedendo e utilizzando il nostro sito web, accetti di rispettare e di essere vincolato da questi Termini di Utilizzo e dalla nostra Informativa sulla Privacy.</p>
    
    <h2>3. Modifiche ai Termini</h2>
    <p>Ci riserviamo il diritto di modificare questi Termini di Utilizzo in qualsiasi momento. Ti informeremo delle modifiche aggiornando la data di ""Ultimo aggiornamento"" riportata all'inizio di questi Termini di Utilizzo.</p>
    
    <h2>4. Responsabilità dell'Utente</h2>
    <p>Accetti di utilizzare il nostro sito web solo per scopi leciti e in modo da non violare i diritti di altri né limitare o inibire il loro utilizzo e godimento del nostro sito web.</p>
    
    <h2>5. Proprietà Intellettuale</h2>
    <p>Tutti i contenuti presenti sul nostro sito web, inclusi testi, grafica, loghi, immagini e software, sono di proprietà di {{ company_name }} e sono protetti dalle leggi applicabili sulla proprietà intellettuale.</p>
    
    <h2>6. Limitazione di Responsabilità</h2>
    <p>Non saremo responsabili per eventuali danni di qualsiasi tipo derivanti dall'uso del nostro sito web, inclusi ma non limitati a danni diretti, indiretti, incidentali, punitivi e consequenziali.</p>
    
    <h2>7. Legge Applicabile</h2>
    <p>Questi Termini di Utilizzo sono regolati e interpretati in conformità con le leggi di {{ country }} e accetti la giurisdizione non esclusiva dei tribunali situati in {{ country }} per la risoluzione di eventuali controversie.</p>
    
    <h2>8. Contattaci</h2>
    <p>Se hai domande su questi Termini di Utilizzo, ti preghiamo di contattarci a {{ contact_information }}.</p>

    """

    # Check if a record already exists
    existing_content = TextContent.query.filter_by(content_type='terms_of_use', language_code='it').first()

    if existing_content:
        # Update the existing record
        existing_content.content_body = content_body
        existing_content.title = 'Termini di utilizzo'
        print("Existing record updated successfully!")
    else:
        # Create a new record
        new_content = TextContent(
            content_type='terms_of_use',
            content_body=content_body,
            language_code='it',
            title='Termini di utilizzo'
        )
        db.session.add(new_content)
        print("New record created successfully!")

    # Commit the changes
    db.session.commit()
