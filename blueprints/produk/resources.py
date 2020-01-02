from flask_restful import Resource, reqparse, marshal, inputs, Api
from flask_jwt_extended import jwt_required, get_jwt_claims
from flask import Blueprint
from blueprints import db, admin_required
from sqlalchemy import desc
from datetime import datetime
from blueprints.produk.model import Products, Reviews, Specifications
import requests


blueprint_product = Blueprint("product", __name__)
api_product = Api(blueprint_product)


class ProductResources(Resource):
    def get(self, id=None):
        if id is None:
            rows = []
            parser =reqparse.RequestParser()
            parser.add_argument("keyword", location="args")
            parser.add_argument("category", location="args")
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
            if args["category"] is not None:
                qry = qry.filter_by(kategori=args["category"])
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
            if qry is None or not qry.status:
                return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}
            detail_product = marshal(qry, Products.response_fields)
            # request specification, lalu append ke query product
            specification_params = {
                "product_id": id
            }
            requested_data = requests.get("http://localhost:5000/product/specification", json=specification_params)
            specification_json = requested_data.json()
            detail_product["specification"] = specification_json
            return detail_product, 200, {"Content-Type": "application/json"}


class SpecificationResources(Resource):
    def get(self):
        rows = []
        parser =reqparse.RequestParser()
        parser.add_argument("product_id", type=int, location="json", required=True)
        args = parser.parse_args()
        
        qry = Specifications.query.filter_by(product_id=args["product_id"])
        for row in qry.all():
            marshal_review = marshal(row, Specifications.response_fields)
            rows.append(marshal_review)
        return rows, 200, {"Content-Type": "application/json"}


api_product.add_resource(ProductResources, "", "/<int:id>")
api_product.add_resource(SpecificationResources, "/specification")