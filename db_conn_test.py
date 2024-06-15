import logging
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://audit_postgres_30051_user:yyRiuB4zY2eiwXp7OI9rKiW4mHGI37Rw@dpg-cpbpj763e1ms739a5be0-a.frankfurt-postgres.render.com/audit_postgres_30051?sslmode=require'

logging.basicConfig(level=logging.DEBUG)

@app.route('/test_db_connection')
def test_db_connection():
    try:
        # Replace with your actual database query
        result = db.session.execute('SELECT 1')
        return 'Database connection successful'
    except Exception as e:
        app.logger.error(f"Database connection error: {e}")
        return f"Database connection error: {e}", 500

if __name__ == '__main__':
    app.run()
