from flask_restful import Resource, reqparse, marshal, inputs, Api
from flask_jwt_extended import jwt_required, get_jwt_claims
from flask import Blueprint
from blueprints import db, admin_required, nonadmin_required
from sqlalchemy import desc
from password_strength import PasswordPolicy
from datetime import datetime
from blueprints.user.model import Users
from blueprints.produk.model import Products
from blueprints.transaction.model import Transactions, Carts
from blueprints.produk.resources import ProductResources
import hashlib, requests


blueprint_user = Blueprint("user", __name__)
api_user = Api(blueprint_user)


class ProfileResources(Resource):
    policy = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1,
        special=1
    )

    @jwt_required
    @nonadmin_required
    def get(self):
        user_claims_data = get_jwt_claims()
        qry = Users.query.get(user_claims_data["id"])
        return marshal(qry, Users.response_fields), 200, {"Content-Type": "application/json"}

    @jwt_required
    @nonadmin_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("nama_depan", location="json", required=True)
        parser.add_argument("nama_belakang", location="json", required=True)
        parser.add_argument("email", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        parser.add_argument("telepon", location="json", required=True)
        parser.add_argument("alamat", location="json", required=True)
        parser.add_argument("kota", location="json", required=True)
        parser.add_argument("provinsi", location="json", required=True)
        parser.add_argument("kode_pos", location="json", type=int, required=True)
        args = parser.parse_args()

        user_claims_data = get_jwt_claims()
        qry = Users.query.get(user_claims_data["id"])
        
        validation = self.policy.test(args["password"])
        if validation == []:
            pwd_digest = hashlib.md5(args["password"].encode()).hexdigest()
            if Users.query.get(user_claims_data["id"]).email != args["email"]:
                if Users.query.filter_by(email=args["email"]).first() is not None:
                    return {"status": "FAILED", "message": "Email already exists"}, 400, {"Content-Type": "application/json"}
            qry.nama_depan = args["nama_depan"]
            qry.nama_belakang = args["nama_belakang"]
            qry.email = args["email"]
            qry.password = pwd_digest
            qry.telepon = args["telepon"]
            qry.alamat = args["alamat"]
            qry.kota = args["kota"]
            qry.provinsi = args["provinsi"]
            qry.kode_pos = args["kode_pos"]
            qry.updated_at = datetime.now()
            db.session.commit()
            return marshal(qry, Users.response_fields), 200, {"Content-Type": "application/json"}
        return {"status": "FAILED", "message": "Password is not accepted"}, 400, {"Content-Type": "application/json"}

    @jwt_required
    @nonadmin_required
    def delete(self):
        user_claims_data = get_jwt_claims()
        qry = Users.query.get(user_claims_data["id"])
        qry.status = False
        db.session.commit()
        return {"message": "Succesfully deleted"}, 200, {"Content-Type": "application/json"}


class TransactionResource(Resource):
    @jwt_required
    @nonadmin_required
    def get(self):
        user_claims_data = get_jwt_claims()
        transaction_qry = Transactions.query.filter_by(user_id=user_claims_data["id"])
        transaction_qry = transaction_qry.filter_by(selesai=False).first()
        if transaction_qry is not None:
            return marshal_transaction, 200, {"Content-Type": "application/json"}
        return {"message": "Transaction is not found"}, 404, {"Content-Type": "application/json"}
    
    @jwt_required
    @nonadmin_required
    def put(self):
        parser =reqparse.RequestParser()
        parser.add_argument("kurir", location="json", required=True)
        parser.add_argument("payment", location="json", required=True)
        args = parser.parse_args()

        user_claims_data = get_jwt_claims()
        transaction_qry = Transactions.query.filter_by(user_id=user_claims_data["id"])
        transaction_qry = transaction_qry.filter_by(selesai=False).first()
        if transaction_qry is not None:
            transaction_qry.shipment_method_id = args["kurir"]
            transaction_qry.payment_method_id = args["payment"]
            db.session.commit()
            return marshal(transaction_qry, Transactions.response_fields), 200, {"Content-Type": "application/json"}
        return {"message": "Transaction is not found"}, 404, {"Content-Type": "application/json"}


class CartResources(Resource):
    # @jwt_required
    # @nonadmin_required
    # def get(self):
    #     user_claims_data = get_jwt_claims()
    #     qry = Users.query.get(user_claims_data["id"])
    #     return marshal(qry, Users.response_fields), 200, {"Content-Type": "application/json"}
    
    @jwt_required
    @nonadmin_required
    def post(self):
        rows = []
        user_id = get_jwt_claims()["id"]
        parser =reqparse.RequestParser()
        parser.add_argument("product_id", type=int, location="json", required=True)
        parser.add_argument("jumlah", type=int, location="json", required=True)
        args = parser.parse_args()

        product_qry = Products.query.get(args["product_id"])
        transaction_qry = Transactions.query.filter_by(user_id=user_id)
        if product_qry.jumlah < args["jumlah"]:
            return {"message": "Out of stock"}, 400, {"Content-Type": "application/json"}
        # tambah transaksi jika semua transaksi user sudah selesai
        if transaction_qry.filter_by(selesai=False).first() is None:
            transaction = Transactions(user_id)
            product_qry.jumlah -= args["jumlah"]
            db.session.add(transaction)
            db.session.commit()
        # tambah detail transaksi untuk transaksi yang baru ditambahkan jika product_id tidak ditemukan
        last_added_transaction = transaction_qry.order_by(Transactions.id.desc()).first()
        cart_qry = Carts.query.filter_by(product_id=args["product_id"])
        cart_qry = cart_qry.filter_by(transaction_id=last_added_transaction.id).first()
        if cart_qry is None:
            cart = Carts(args["produk_id"], last_added_transaction.id, args["jumlah"], product_qry.harga*args["jumlah"])
            db.session.add(cart)
            db.session.commit()
        # update detail produk (jumlah, subtotal) dan transaksi (total_tagihan) jika product_id ditemukan
        else:
            pass
        return marshal(cart_qry, Carts.response_fields), 200, {"Content-Type": "application/json"}


api_user.add_resource(ProductResources, "/product", "/product/<int:id>")
api_user.add_resource(ProfileResources, "/profile")