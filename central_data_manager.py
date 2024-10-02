from db import db

class CentralDataManager:
    def __init__(self):
        self.db = db
        self.db.create_tables()
        self.db.drop_tables()


def insert_data(data):
    # Connect to the database
    # conn = sqlite3.connect('data.db')
    # cursor = conn.cursor()

    # Set default value for DimensionID
    default_dimension_id = 0

    # Modify dictionary to include default DimensionID values
    for key, value in data.items():
        if key in ['TopicID', 'SubtopicID', 'Dimension1ID', 'Dimension2ID', 'Dimension3ID', 'Dimension4ID', 'Dimension5ID', 'Dimension6ID', 'Dimension7ID'] and value is None:
            data[key] = default_dimension_id

    # Prepare the INSERT statement
    insert_statement = 'INSERT INTO CentralData (IntervalID, Date, StatusID, UserID, ArealD, TopiciD, SubtopicID, JSON, CreatedOn, CreatedBy) VALUES (?,?,?,?,?,?,?,?,?,?)'

    # Execute the INSERT statement with the modified data
    cursor.execute(insert_statement, data.values())

    # Commit the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()