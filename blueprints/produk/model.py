from blueprints import db
from flask_restful import fields
from datetime import datetime


class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False, default="")
    harga = db.Column(db.Integer, nullable=False, default=0)
    jumlah = db.Column(db.Integer, nullable=False, default=1)
    kategori = db.Column(db.String(100), nullable=False, default="Komponen & Peralatan")
    rating = db.Column(db.Float, nullable=False, default=0)
    deskripsi = db.Column(db.String(200), nullable=False, default="")
    status = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "nama": fields.String,
        "harga": fields.Integer,
        "jumlah": fields.Integer,
        "kategori": fields.String,
        "rating": fields.Float,
        "deskripsi": fields.String,
        "status": fields.Boolean
    }
    
    def __init__(self, nama, harga, kategori, deskripsi):
        self.nama = nama
        self.harga = harga
        self.kategori = kategori
        self.deskripsi = deskripsi

    def __repr__(self):
        return "<Products %r>" % self.id