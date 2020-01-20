from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token
from blueprints import db
from blueprints.user.model import Users
from password_strength import PasswordPolicy
import hashlib

blueprint_auth = Blueprint("auth", __name__)
api = Api(blueprint_auth)

class CreateTokenResources(Resource):
    policy = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1,
        special=1
    )

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        args = parser.parse_args()
        print(args)
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
        return {
            "token": token, "admin": user_claims_data["is_admin"], "message": "Token is successfully created"
        }, 200, {"Content-Type": "application/json"}
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("nama_depan", location="json", required=True)
        parser.add_argument("nama_belakang", location="json", required=True)
        parser.add_argument("email", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        args = parser.parse_args()
        password = hashlib.md5(args["password"].encode()).hexdigest()
        args = parser.parse_args()
        validation = self.policy.test(args["password"])
        if validation == []:
            pwd_digest = hashlib.md5(args["password"].encode()).hexdigest()
            user = Users(args["nama_depan"], args["nama_belakang"], args["email"], pwd_digest)
            if Users.query.filter_by(email=args["email"]).all() != []:
                return {"status": "FAILED", "message": "Email already exists"}, 400, {"Content-Type": "application/json"}
            db.session.add(user)
            db.session.commit()
            return marshal(user, Users.response_fields), 200, {"Content-Type": "application/json"}
        return {"status": "FAILED", "message": "Password is not accepted"}, 400, {"Content-Type": "application/json"}

    def options(self):
        return 200


api.add_resource(CreateTokenResources, "")