from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, nonadmin_required
from sqlalchemy import desc
from datetime import datetime
from blueprints.produk.model import *


blueprint_produk = Blueprint("produk", __name__)
api_produk = Api(blueprint_produk)


class ProductResources(Resource):
    def get(self, id=None):
        if id is None:
            rows = []
            parser =reqparse.RequestParser()
            parser.add_argument("keyword", location="args")
            parser.add_argument("category", location="args")
            parser.add_argument("lower_price", type=int, location="args")
            parser.add_argument("upper_price", type=int, location="args")
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
                qry = qry.filter(Products.nama.like("%"+args["title"]+"%"))
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
            if total_entry%per_page != 0 or total_entry == 0: total_page = int(total_entry/per_page) + 1
            else: total_page = int(total_entry/per_page)
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
            return marshal(qry, Products.response_fields), 200, {"Content-Type": "application/json"}


api_produk.add_resource(ProductResources, "", "/<int:id>")