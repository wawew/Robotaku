from flask_restful import Resource, reqparse, marshal, inputs, Api
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required
from flask import Blueprint
from sqlalchemy import or_
from datetime import datetime
from blueprints.produk.model import Products, Reviews, Specifications
from blueprints.user.model import Users
from blueprints.transaction.model import ShipmentMethods, PaymentMethods, Transactions, Carts
import requests


blueprint_admin = Blueprint("admin", __name__)
api_admin = Api(blueprint_admin)


class ProductManagementResources(Resource):
    @jwt_required
    @admin_required
    def get(self, id=None):
        if id is None:
            rows = []
            parser =reqparse.RequestParser()
            parser.add_argument("keyword", location="args")
            parser.add_argument("kategori", location="args")
            parser.add_argument("lower_price", type=int, location="args", default=0)
            parser.add_argument("upper_price", type=int, location="args", default=999999999999999)
            parser.add_argument("rating", type=int, location="args")
            parser.add_argument("p", type=int, location="args", default=1)
            parser.add_argument("rp", type=int, location="args", default=12)
            parser.add_argument("status", location="args", type=inputs.boolean)
            args = parser.parse_args()
            offset = (args["p"] - 1)*args["rp"]
            
            qry = Products.query
            if args["status"] is not None:
                qry = qry.filter_by(status=args["status"])
            if args["kategori"] is not None:
                qry = qry.filter_by(kategori=args["kategori"])
            if args["keyword"] is not None:
                qry = qry.filter(Products.nama.like("%"+args["keyword"]+"%"))
            if args["lower_price"] is not None:
                qry = qry.filter(Products.harga >= args["lower_price"])
            if args["upper_price"] is not None:
                qry = qry.filter(Products.harga <= args["upper_price"])
            if args["rating"] is not None:
                qry = qry.filter(Products.rating >= args["rating"])
            
            total_entry = len(qry.all())
            qry = qry.limit(args["rp"]).offset(offset)

            if total_entry%args["rp"] != 0 or total_entry == 0: total_page = int(total_entry/args["rp"]) + 1
            else: total_page = int(total_entry/args["rp"])
            result_json = {
                "total_entry": total_entry, "page":args["p"], "total_page":total_page, "per_page":args["rp"]
            }
            
            for row in qry.all():
                marshal_product = marshal(row, Products.response_fields)
                rows.append(marshal_product)
            marshal_out["data"] = rows
            return marshal_out, 200, {"Content-Type": "application/json"}
        else:
            qry = Products.query.get(id)
            if qry is None:
                return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}
            detail_product = marshal(qry, Products.response_fields)
            spec_rev_params = {"product_id": id}
            # request specification, lalu append ke query product
            requested_data = requests.get("http://localhost:5000/product/specification", json=spec_rev_params)
            specification_json = requested_data.json()
            detail_product["specification"] = specification_json
            # request review, lalu append ke query product
            requested_data = requests.get("http://localhost:5000/product/review", json=spec_rev_params)
            review_json = requested_data.json()
            detail_product["reviews"] = review_json
            return detail_product, 200, {"Content-Type": "application/json"}

    @jwt_required
    @admin_required
    def post(self):
        parser =reqparse.RequestParser()
        parser.add_argument("nama", location="json", required=True)
        parser.add_argument("harga", type=int, location="json", required=True)
        parser.add_argument("kategori", location="json", required=True)
        parser.add_argument("deskripsi", location="json", required=True)
        args = parser.parse_args()
        product = Products(args["nama"], args["harga"], args["kategori"], args["deskripsi"])
        db.session.add(product)
        db.session.commit()
        return marshal(product, Products.response_fields), 200, {"Content-Type": "application/json"}
    
    @jwt_required
    @admin_required
    def put(self, id=None):
        parser =reqparse.RequestParser()
        parser.add_argument("nama", location="json")
        parser.add_argument("harga", type=int, location="json")
        parser.add_argument("jumlah", type=int, location="json")
        parser.add_argument("kategori", location="json")
        parser.add_argument("deskripsi", location="json")
        parser.add_argument("status", type=inputs.boolean, location="json")
        args = parser.parse_args()
        if id is not None:
            qry = Products.query.get(id)
            if qry is not None:
                if args["nama"] is not None:
                    qry.nama = args["nama"]
                if args["harga"] is not None:
                    qry.harga = args["harga"]
                if args["jumlah"] is not None:
                    qry.jumlah = args["jumlah"]
                if args["kategori"] is not None:
                    qry.kategori = args["kategori"]
                if args["deskripsi"] is not None:
                    qry.deskripsi = args["deskripsi"]
                if args["status"] is not None:
                    qry.status = args["status"]
                qry.updated_at = datetime.now()
                db.session.commit()
                return marshal(qry, Products.response_fields), 200, {"Content-Type": "application/json"}
        return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}


class SpecificationManagementResources(Resource):
    @jwt_required
    @admin_required
    def post(self):
        parser =reqparse.RequestParser()
        parser.add_argument("product_id", location="json", required=True)
        parser.add_argument("content", location="json", required=True)
        args = parser.parse_args()
        
        qry = Products.query.get(args["product_id"])
        if qry is not None:
            specification = Specifications(args["product_id"], args["content"])
            db.session.add(specification)
            db.session.commit()
            return marshal(specification, Specifications.response_fields), 200, {"Content-Type": "application/json"}
        return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}
    
    @jwt_required
    @admin_required
    def put(self, id=None):
        parser =reqparse.RequestParser()
        parser.add_argument("content", location="json", required=True)
        args = parser.parse_args()
        
        if id is not None:
            qry = Specifications.query.get(id)
            if qry is not None:
                qry.content = args["content"]
                qry.updated_at = datetime.now()
                db.session.commit()
                return marshal(qry, Specifications.response_fields), 200, {"Content-Type": "application/json"}
        return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}


class UserManagementResources(Resource):
    @jwt_required
    @admin_required
    def get(self, id=None):
        if id is None:
            parser =reqparse.RequestParser()
            parser.add_argument("nama_depan", location="args")
            parser.add_argument("nama_belakang", location="args")
            parser.add_argument("email", location="args")
            parser.add_argument("telepon", location="args")
            parser.add_argument("alamat", location="args")
            parser.add_argument("kota", location="args")
            parser.add_argument("provinsi", location="args")
            parser.add_argument("kode_pos", location="args")
            parser.add_argument("status", location="args", type=inputs.boolean)
            parser.add_argument("p", type=int, location="args", default=1)
            parser.add_argument("rp", type=int, location="args", default=12)
            args = parser.parse_args()
            offset = (args["p"] - 1)*args["rp"]
            
            user_qry = Users.query
            if args["status"] is not None:
                user_qry = user_qry.filter_by(status=args["status"])
            if args["nama_depan"] is not None:
                user_qry = user_qry.filter(Users.nama_depan.like("%"+args["nama_depan"]+"%"))
            if args["nama_belakang"] is not None:
                user_qry = user_qry.filter(Users.nama_belakang.like("%"+args["nama_belakang"]+"%"))
            if args["email"] is not None:
                user_qry = user_qry.filter(Users.email.like("%"+args["email"]+"%"))
            if args["telepon"] is not None:
                user_qry = user_qry.filter(Users.telepon.like("%"+args["telepon"]+"%"))
            if args["alamat"] is not None:
                user_qry = user_qry.filter(Users.alamat.like("%"+args["alamat"]+"%"))
            if args["kota"] is not None:
                user_qry = user_qry.filter(Users.kota.like("%"+args["kota"]+"%"))
            if args["provinsi"] is not None:
                user_qry = user_qry.filter(Users.provinsi.like("%"+args["provinsi"]+"%"))
            if args["kode_pos"] is not None:
                user_qry = user_qry.filter(Users.kode_pos.like("%"+args["kode_pos"]+"%"))
            
            total_entry = len(user_qry.all())
            user_qry = user_qry.limit(args["rp"]).offset(offset)

            if total_entry%args["rp"] != 0 or total_entry == 0: total_page = int(total_entry/args["rp"]) + 1
            else: total_page = int(total_entry/args["rp"])
            result_json = {
                "total_entry": total_entry, "page":args["p"], "total_page":total_page, "per_page":args["rp"]
            }
            
            rows = []
            for row in user_qry.all():
                marshal_user = marshal(row, Users.response_fields)
                rows.append(marshal_user)
            marshal_out["data"] = rows
            return marshal_out, 200, {"Content-Type": "application/json"}
        else:
            user_qry = Users.query.get(id)
            if user_qry is None:
                return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}
            detail_user = marshal(user_qry, Users.response_fields)
            return detail_user, 200, {"Content-Type": "application/json"}
        
    @jwt_required
    @admin_required
    def put(self, id=None):
        parser =reqparse.RequestParser()
        parser.add_argument("status", location="json", type=inputs.boolean)
        args = parser.parse_args()
        if id is not None:
            user_qry = Users.query.get(id)
            if args["status"] is not None and user_qry is not None:
                user_qry.status = args["status"]
                detail_user = marshal(user_qry, Users.response_fields)
                return detail_user, 200, {"Content-Type": "application/json"}
        return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}


class TransactionManagementResources(Resource):
    @jwt_required
    @admin_required
    def get(self, id=None):
        parser =reqparse.RequestParser()
        parser.add_argument("user_id", type=int, location="args")
        parser.add_argument("pembayaran", location="args")
        parser.add_argument("kurir", location="args")
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
                shipment_method_qry = ShipmentMethods.query.get(marshal_transaction["shipment_method_id"])
                payment_method_qry = PaymentMethods.query.get(marshal_transaction["payment_method_id"])
                marshal_transaction["nama_pengguna"] = Users.query.get(transaction_qry.user_id)
                if marshal_transaction["status"] == "staging":
                    marshal_transaction["shipment_method"] = None
                    marshal_transaction["payment_method"] = None
                else:
                    marshal_transaction["shipment_method"] = marshal(shipment_method_qry, ShipmentMethods.response_fields)
                    marshal_transaction["payment_method"] = marshal(payment_method_qry, PaymentMethods.response_fields)
                del marshal_transaction["shipment_method_id"]
                del marshal_transaction["payment_method_id"]
                return marshal_transaction, 200, {"Content-Type": "application/json"}
        # show all filtered transaction history
        else:
            transaction_qry = Transactions.query
            if args["status"] is not None:
                transaction_qry = transaction_qry.filter_by(status=args["status"])
            if args["user_id"] is not None:
                transaction_qry = transaction_qry.filter_by(user_id=args["user_id"])
            if args["pembayaran"] is not None:
                transaction_qry = transaction_qry.filter(Users.nama_belakang.like("%"+args["pembayaran"]+"%"))
            if args["kurir"] is not None:
                transaction_qry = transaction_qry.filter(Users.nama_belakang.like("%"+args["kurir"]+"%"))
            
            total_entry = len(transaction_qry.all())
            transaction_qry = transaction_qry.limit(args["rp"]).offset(offset)
            
            if total_entry%args["rp"] != 0 or total_entry == 0: total_page = int(total_entry/args["rp"]) + 1
            else: total_page = int(total_entry/args["rp"])
            result_json = {
                "total_entry": total_entry, "page":args["p"], "total_page":total_page, "per_page":args["rp"]
            }
            rows = []
            for each_transaction in transaction_qry.all():
                marshal_transaction = marshal(each_transaction, Transactions.response_fields)
                shipment_method_qry = ShipmentMethods.query.get(marshal_transaction["shipment_method_id"])
                payment_method_qry = PaymentMethods.query.get(marshal_transaction["payment_method_id"])
                if marshal_transaction["status"] == "staging":
                    marshal_transaction["shipment_method"] = None
                    marshal_transaction["payment_method"] = None
                else:
                    marshal_transaction["shipment_method"] = shipment_method_qry.kurir
                    marshal_transaction["payment_method"] = payment_method_qry.nama
                del marshal_transaction["shipment_method_id"]
                del marshal_transaction["payment_method_id"]
                rows.append(marshal_transaction)
            result_json["transaction"] = rows
            return result_json, 200, {"Content-Type": "application/json"}
        return {"message": "Transaction is not found"}, 404, {"Content-Type": "application/json"}


api_admin.add_resource(ProductManagementResources, "/product", "/product/<int:id>")
api_admin.add_resource(SpecificationManagementResources, "/product/specification", "/product/specification/<int:id>")
api_admin.add_resource(UserManagementResources, "/user", "/user/<int:id>")
api_admin.add_resource(TransactionManagementResources, "/transaction", "/transaction/<int:id>")
