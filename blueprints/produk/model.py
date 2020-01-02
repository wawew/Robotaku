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


class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_rating = db.Column(db.Float, nullable=False, default=0)
    content = db.Column(db.String(200), nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "product_id": fields.Integer,
        "user_id": fields.Integer,
        "user_rating": fields.Float,
        "content": fields.String
    }
    
    def __init__(self, product_id, user_id, user_rating, content):
        self.product_id = product_id
        self.user_id = user_id
        self.user_rating = user_rating
        self.content = content

    def __repr__(self):
        return "<Reviews %r>" % self.id


class Specifications(db.Model):
    __tablename__ = "specifications"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    
    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "product_id": fields.Integer,
        "content": fields.String
    }
    
    def __init__(self, product_id, content):
        self.product_id = product_id
        self.content = content

    def __repr__(self):
        return "<Specifications %r>" % self.id