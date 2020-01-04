from blueprints import db
from flask_restful import fields
from datetime import datetime


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_depan = db.Column(db.String(100), nullable=False)
    nama_belakang = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    telepon = db.Column(db.String(15), unique=True)
    alamat = db.Column(db.String(100), nullable=False, default="")
    kota = db.Column(db.String(20), nullable=False, default="")
    provinsi = db.Column(db.String(20), nullable=False, default="")
    kode_pos = db.Column(db.String(10), nullable=False, default="")
    status = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "nama_depan": fields.String,
        "nama_belakang": fields.String,
        "email": fields.String,
        "password": fields.String,
        "telepon": fields.String,
        "alamat": fields.String,
        "kota": fields.String,
        "provinsi": fields.String,
        "kode_pos": fields.String,
        "status": fields.Boolean
    }

    jwt_claim_fields = {
        "id": fields.Integer,
        "email": fields.String,
        "is_admin": fields.Boolean
    }

    def __init__(self, nama_depan, nama_belakang, email, password):
        self.nama_depan = nama_depan
        self.nama_belakang = nama_belakang
        self.email = email
        self.password = password

    def __repr__(self):
        return "<Users %r>" % self.id