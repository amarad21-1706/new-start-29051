from app_factory import db

class CentralData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    interval_id = db.Column(db.Integer)
    reference_date = db.Column(db.String(255))
    status_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    type_id = db.Column(db.String(255))
    topic_id = db.Column(db.String(128))
    topic1_id = db.Column(db.String(128))
    topic2_id = db.Column(db.String(128))
    topic3_id = db.Column(db.String(128))
    dimension1_id = db.Column(db.Integer)
    dimension2_id = db.Column(db.Integer)
    dimension3_id = db.Column(db.Integer)
    dimension4_id = db.Column(db.Integer)
    dimension5_id = db.Column(db.Integer)
    dimension6_id = db.Column(db.Integer)
    dimension7_id = db.Column(db.Integer)
    extended_data = db.Column(db.JSON)
    created_on = db.Column(db.DateTime)
    created_by = db.Column(db.String(255))

    def __repr__(self):
      return f'<CentralData {self.interval_id}>'
