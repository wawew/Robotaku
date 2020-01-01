from blueprints import db
from flask_restful import fields
from datetime import datetime

class Watchlists(db.Model):
    __tablename__ = "watchlists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    movie_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "user_id": fields.Integer,
        "movie_id": fields.Integer
    }

    def __init__(self, user_id, movie_id):
        self.user_id = user_id,
        self.movie_id = movie_id

    def __repr__(self):
        return "<Watchlists %r>" % self.id