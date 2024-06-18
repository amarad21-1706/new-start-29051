# not working
import sqlite3
import json
from app.modules.db import db
import os

# Connect to the SQLite database
current_directory = os.getcwd()
print(current_directory)
# Extract /config part
config_directory = os.path.normpath(os.path.join(current_directory, 'config'))
# Other configurations

# SQLite
sqlite_conn = sqlite3.connect('///{current_directory}/database/sysconfig.db')
cursor = sqlite_conn.cursor()

# Query to get JSON data from the SQLite table
cursor.execute("SELECT json_field FROM your_sqlite_table")
rows = cursor.fetchall()

# Save JSON data to a file
with open('data.json', 'w') as json_file:
    json.dump([row[0] for row in rows], json_file)

# Close the SQLite connection
sqlite_conn.close()

with app.app_context():
    bind_key = 'db1'  # Use the bind key corresponding to the desired database

    options = {'url': str(db.engine.url)}  # Your options dictionary

    # Create the SQLAlchemy engine using db object
    engine = db._make_engine(bind_key, options, app)
    # Usage example:
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    session = Session()  # Create a session object
