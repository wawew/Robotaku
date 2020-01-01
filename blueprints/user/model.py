from blueprints import db
from flask_restful import fields
from datetime import datetime


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    telepon = db.Column(db.String(15), unique=True, nullable=False, default="")
    alamat = db.Column(db.String(100), nullable=False, default="")
    kota = db.Column(db.String(20), nullable=False, default="")
    provinsi = db.Column(db.String(20), nullable=False, default="")
    kode_pos = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "email": fields.String,
        "telepon": fields.String,
        "password": fields.String,
        "status": fields.Boolean
    }

    jwt_claim_fields = {
        "id": fields.Integer,
        "email": fields.String,
        "is_admin": fields.Boolean
    }

    def __init__(self, email, secret):
        self.email = email
        self.password = secret

    def __repr__(self):
        return "<Users %r>" % self.id