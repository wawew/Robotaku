from flask_restful import Resource, reqparse, marshal, inputs, Api
from flask_jwt_extended import jwt_required, get_jwt_claims
from flask import Blueprint
from blueprints import db, admin_required, nonadmin_required
# from sqlalchemy import desc
from password_strength import PasswordPolicy
from datetime import datetime
from blueprints.user.model import Users
from blueprints.produk.model import Products
from blueprints.transaction.model import Transactions, Carts, PaymentMethods, ShipmentMethods
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
            if qry.email != args["email"]:
                if Users.query.filter_by(email=args["email"]).first() is not None:
                    return {"status": "FAILED", "message": "Email already exists"}, 400, {"Content-Type": "application/json"}
            if qry.telepon != args["telepon"]:
                if Users.query.filter_by(telepon=args["telepon"]).first() is not None:
                    return {"status": "FAILED", "message": "Phone already exists"}, 400, {"Content-Type": "application/json"}
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
    def get(self, id=None):
        parser =reqparse.RequestParser()
        parser.add_argument("status", location="args")
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=5)
        args = parser.parse_args()
        offset = (args["p"] - 1)*args["rp"]

        # show selected transaction history
        if id is not None:
            transaction_qry = Transactions.query.get(id)
            if transaction_qry is not None:
                marshal_transaction = marshal(transaction_qry, Transactions.response_fields)
                return marshal_transaction, 200, {"Content-Type": "application/json"}
        # show all filtered transaction history
        else:
            user_claims_data = get_jwt_claims()
            transaction_qry = Transactions.query.filter_by(user_id=user_claims_data["id"])
            if args["status"] is not None:
                transaction_qry = transaction_qry.filter_by(status=args["status"])
            transaction_qry = transaction_qry.limit(args["rp"]).offset(offset)
            
            total_entry = len(transaction_qry.all())
            if total_entry%args["rp"] != 0 or total_entry == 0: total_page = int(total_entry/args["rp"]) + 1
            else: total_page = int(total_entry/args["rp"])
            result_json = {"page":args["p"], "total_page":total_page, "per_page":args["rp"]}
            rows = []
            for each_transaction in transaction_qry.all():
                marshal_transaction = marshal(each_transaction, Transactions.response_fields)
                rows.append(marshal_transaction)
            result_json["transaction"] = rows
            print(result_json)
            return result_json, 200, {"Content-Type": "application/json"}
        return {"message": "Transaction is not found"}, 404, {"Content-Type": "application/json"}


class ShipmentResource(Resource):
    @jwt_required
    @nonadmin_required
    def get(self):
        parser =reqparse.RequestParser()
        parser.add_argument("shipment_method_id", type=int, location="json", required=True)
        parser.add_argument("payment_method_id", type=int, location="json", required=True)
        args = parser.parse_args()

        user_claims_data = get_jwt_claims()
        transaction_qry = Transactions.query.filter_by(user_id=user_claims_data["id"])
        transaction_qry = transaction_qry.filter_by(status="staging").first()
        if transaction_qry is not None:
            result_json = {}
            user_qry = Users.query.get(user_claims_data["id"])
            shipment_price = ShipmentMethods.query.get(args["shipment_method_id"]).tarif
            payment_price = PaymentMethods.query.get(args["payment_method_id"]).tarif
            result_json["alamat_lengkap"] = {
                "alamat": user_qry.alamat,
                "kota": user_qry.kota,
                "provinsi": user_qry.provinsi,
                "kode_pos": user_qry.kode_pos
            }
            cart_qry = Carts.query.filter_by(transaction_id=transaction_qry.id)
            result_json["total_product"] = len(cart_qry.all())
            result_json["total_harga"] = transaction_qry.total_harga
            result_json["tarif_pengiriman"] = shipment_price
            result_json["tarif_pembayaran"] = payment_price
            result_json["total_tagihan"] = transaction_qry.total_harga+shipment_price+payment_price
            return result_json, 200, {"Content-Type": "application/json"}
        return {"message": "Transaction is not found"}, 404, {"Content-Type": "application/json"}

    @jwt_required
    @nonadmin_required
    def put(self):
        parser =reqparse.RequestParser()
        parser.add_argument("shipment_method_id", type=int, location="json", required=True)
        parser.add_argument("payment_method_id", type=int, location="json", required=True)
        args = parser.parse_args()

        shipment_price = ShipmentMethods.query.get(args["shipment_method_id"]).tarif
        payment_price = PaymentMethods.query.get(args["payment_method_id"]).tarif
        user_claims_data = get_jwt_claims()
        transaction_qry = Transactions.query.filter_by(user_id=user_claims_data["id"])
        transaction_qry = transaction_qry.filter_by(status="staging").first()
        if transaction_qry is not None:
            transaction_qry.status = "waiting"
            transaction_qry.shipment_method_id = args["shipment_method_id"]
            transaction_qry.payment_method_id = args["payment_method_id"]
            transaction_qry.total_tagihan = transaction_qry.total_harga+shipment_price+payment_price
            transaction_qry.updated_at = datetime.now()
            db.session.commit()
            return marshal(transaction_qry, Transactions.response_fields), 200, {"Content-Type": "application/json"}
        return {"message": "Transaction is not found"}, 404, {"Content-Type": "application/json"}


class CartResources(Resource):
    @jwt_required
    @nonadmin_required
    # tampilkan hanya jika transaksi masih pada tahap staging
    def get(self):
        rows = []
        user_claims_data = get_jwt_claims()
        transaction_qry = Transactions.query.filter_by(user_id=user_claims_data["id"])
        transaction_qry = transaction_qry.filter_by(status="staging").first()
        if transaction_qry is not None:
            cart_qry = Carts.query.filter_by(transaction_id=transaction_qry.id)
            for each_item in cart_qry.all():
                marshal_cart = marshal(each_item, Carts.response_fields)
                rows.append(marshal_cart)
            return rows, 200, {"Content-Type": "application/json"}
        return {"message": "Your cart is empty"}, 404, {"Content-Type": "application/json"}
    
    @jwt_required
    @nonadmin_required
    def post(self):
        user_claims_data = get_jwt_claims()
        parser =reqparse.RequestParser()
        parser.add_argument("product_id", type=int, location="json", required=True)
        parser.add_argument("jumlah", type=int, location="json", required=True)
        args = parser.parse_args()

        product_qry = Products.query.get(args["product_id"])
        transaction_qry = Transactions.query.filter_by(user_id=user_claims_data["id"])
        if transaction_qry.filter_by(status="waiting").first() is not None:
            return {"message": "Please complete your payment"}, 400, {"Content-Type": "application/json"}
        if product_qry.jumlah < args["jumlah"]:
            return {"message": "Out of stock"}, 400, {"Content-Type": "application/json"}
        
        # tambah transaksi jika semua transaksi user sudah selesai
        if transaction_qry.filter_by(status="staging").first() is None:
            transaction = Transactions(user_claims_data["id"])
            db.session.add(transaction)
            
        # tambah detail transaksi untuk transaksi yang baru ditambahkan jika product_id tidak ditemukan di cart
        last_added_transaction = transaction_qry.order_by(Transactions.id.desc()).first()
        cart_qry = Carts.query.filter_by(product_id=args["product_id"])
        cart_qry = cart_qry.filter_by(transaction_id=last_added_transaction.id).first()
        if cart_qry is None:
            cart = Carts(args["product_id"], last_added_transaction.id, args["jumlah"], product_qry.harga*args["jumlah"])
            db.session.add(cart)
        # update detail produk (jumlah, subtotal) jika product_id ditemukan
        else:
            cart_qry.jumlah = args["jumlah"]
            cart_qry.subtotal = args["jumlah"]*product_qry.harga
            cart_qry.updated_at = datetime.now()
        
        total_price = 0
        for each_item in Carts.query.filter_by(transaction_id=last_added_transaction.id).all():
            total_price += each_item.subtotal
        # update transaksi (total_tagihan, total_harga)
        last_added_transaction.total_harga = total_price
        last_added_transaction.updated_at = datetime.now()
        db.session.commit()
        return marshal(last_added_transaction, Transactions.response_fields), 200, {"Content-Type": "application/json"}


api_user.add_resource(ProductResources, "/product", "/product/<int:id>")
api_user.add_resource(ProfileResources, "/profile")
api_user.add_resource(CartResources, "/cart")
api_user.add_resource(ShipmentResource, "/shipment")
api_user.add_resource(TransactionResource, "/transaction", "/transaction/<int:id>")