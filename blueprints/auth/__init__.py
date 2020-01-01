from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token
from blueprints.user.model import *
import hashlib

blueprint_auth = Blueprint("auth", __name__)
api = Api(blueprint_auth)

class CreateTokenResources(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        args = parser.parse_args()
        password = hashlib.md5(args["password"].encode()).hexdigest()
        if args["email"] == "admin@robotaku.id" and args["password"] == "W@wew123":
            user_claims_data = {}
            user_claims_data["is_admin"] = True
        else:
            qry = Users.query.filter_by(email=args["email"])
            qry = qry.filter_by(password=password)
            qry = qry.filter_by(status=True).first()
            if qry is None:
                return {"status": "UNAUTHORIZED", "message": "Invalid email or password"}, 401, {"Content-Type": "application/json"}
            user_claims_data = marshal(qry, Users.jwt_claim_fields)
            user_claims_data["is_admin"] = False
        token = create_access_token(identity=args["email"], user_claims=user_claims_data)
        return {"token": token, "message": "Token is successfully created"}, 200, {"Content-Type": "application/json"}

api.add_resource(CreateTokenResources, "")