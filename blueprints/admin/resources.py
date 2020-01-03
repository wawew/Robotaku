from flask_restful import Resource, reqparse, marshal, inputs, Api
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required
from flask import Blueprint
from sqlalchemy import desc
from datetime import datetime
from blueprints.produk.model import Products, Reviews, Specifications
import requests


blueprint_admin = Blueprint("admin", __name__)
api_admin = Api(blueprint_admin)


class ProductResources(Resource):
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
            if args["keyword"] is not None:
                qry = qry.filter(Products.nama.like("%"+args["keyword"]+"%"))
            if args["kategori"] is not None:
                qry = qry.filter_by(kategori=args["kategori"])
            if args["lower_price"] is not None:
                qry = qry.filter(Products.harga >= args["lower_price"])
            if args["upper_price"] is not None:
                qry = qry.filter(Products.harga <= args["upper_price"])
            if args["rating"] is not None:
                qry = qry.filter(Products.rating >= args["rating"])
            qry = qry.limit(args["rp"]).offset(offset)

            total_entry = len(qry.all())
            if total_entry%args["rp"] != 0 or total_entry == 0: total_page = int(total_entry/args["rp"]) + 1
            else: total_page = int(total_entry/args["rp"])
            marshal_out = {"page":args["p"], "total_page":total_page, "per_page":args["rp"]}
            
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


class SpecificationResources(Resource):
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


api_admin.add_resource(ProductResources, "/product", "/product/<int:id>")
api_admin.add_resource(SpecificationResources, "/product/specification", "/product/specification/<int:id>")