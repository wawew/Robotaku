from flask_restful import Resource, reqparse, marshal, inputs, Api
from flask_jwt_extended import jwt_required, get_jwt_claims
from flask import Blueprint
from blueprints import db, admin_required
from sqlalchemy import desc
from datetime import datetime
from blueprints.produk.model import Products, Reviews, Specifications
from blueprints.user.model import Users
import requests


blueprint_product = Blueprint("product", __name__)
api_product = Api(blueprint_product)


class ProductResources(Resource):
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
            args = parser.parse_args()
            offset = (args["p"] - 1)*args["rp"]
            
            qry = Products.query.filter_by(status=True)
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
            result_json["data"] = rows
            return result_json, 200, {"Content-Type": "application/json"}
        else:
            qry = Products.query.get(id)
            if qry is None or not qry.status:
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


class SpecificationResources(Resource):
    def get(self):
        rows = []
        parser =reqparse.RequestParser()
        parser.add_argument("product_id", type=int, location="json", required=True)
        args = parser.parse_args()
        
        qry = Specifications.query.filter_by(product_id=args["product_id"])
        for row in qry.all():
            marshal_specification = marshal(row, Specifications.response_fields)
            rows.append(marshal_specification)
        return rows, 200, {"Content-Type": "application/json"}


class ReviewResources(Resource):
    def get(self):
        rows = []
        parser =reqparse.RequestParser()
        parser.add_argument("product_id", type=int, location="json", required=True)
        parser.add_argument("rating", type=int, location="json")
        parser.add_argument("p", type=int, location="json", default=1)
        parser.add_argument("rp", type=int, location="json", default=3)
        args = parser.parse_args()
        offset = (args["p"] - 1)*args["rp"]
        
        qry = Reviews.query.filter_by(product_id=args["product_id"])
        qry = qry.order_by(Reviews.updated_at.desc())
        if args["rating"] is not None:
            qry = qry.filter(Reviews.rating >= args["rating"])
        
        total_entry = len(qry.all())
        qry = qry.limit(args["rp"]).offset(offset)

        if total_entry%args["rp"] != 0 or total_entry == 0: total_page = int(total_entry/args["rp"]) + 1
        else: total_page = int(total_entry/args["rp"])
        result_json = {
            "total_entry": total_entry, "page":args["p"], "total_page":total_page, "per_page":args["rp"]
        }
        
        for row in qry.all():
            marshal_review = marshal(row, Reviews.response_fields)
            qry_user = Users.query.get(marshal_review["user_id"])
            if qry_user is not None:
                marshal_review["user_fullname"] = qry_user.nama_depan+" "+qry_user.nama_belakang
                rows.append(marshal_review)
        result_json["data"] = rows
        return result_json, 200, {"Content-Type": "application/json"}


api_product.add_resource(ProductResources, "", "/<int:id>")
api_product.add_resource(SpecificationResources, "/specification")
api_product.add_resource(ReviewResources, "/review")