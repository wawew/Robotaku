from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, nonadmin_required
from sqlalchemy import desc
from password_strength import PasswordPolicy
from datetime import datetime
from blueprints.user.model import *
import hashlib


blueprint_admin = Blueprint("admin", __name__)
api_admin = Api(blueprint_admin)
blueprint_user = Blueprint("user", __name__)
api_user = Api(blueprint_user)

class AdminResources(Resource):
    policy = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1,
        special=1
    )

    @jwt_required
    @admin_required
    def get(self, id=None):
        if id is None:
            rows = []
            parser =reqparse.RequestParser()
            parser.add_argument("p", type=int, location="args", default=1)
            parser.add_argument("rp", type=int, location="args", default=25)
            parser.add_argument("status", location="args", type=inputs.boolean)
            args = parser.parse_args()
            offset = (args["p"] - 1)*args["rp"]
            
            qry = Users.query
            if args["status"] is not None:
                qry = qry.filter_by(status=args["status"])
            qry = qry.limit(args["rp"]).offset(offset)
            for row in qry.all():
                rows.append(marshal(row, Users.response_fields))
            return rows, 200, {"Content-Type": "application/json"}
        else:
            qry = Users.query.get(id)
            if qry is None:
                return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}
            return marshal(qry, Users.response_fields), 200, {"Content-Type": "application/json"}

    @jwt_required
    @admin_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        args = parser.parse_args()
        validation = self.policy.test(args["password"])
        if validation == []:
            pwd_digest = hashlib.md5(args["password"].encode()).hexdigest()
            user = Users(args["username"], pwd_digest)
            if Users.query.filter_by(username=args["username"]).all() != []:
                return {"status": "FAILED", "message": "Username already exists"}, 400, {"Content-Type": "application/json"}
            db.session.add(user)
            db.session.commit()
            return marshal(user, Users.response_fields), 200, {"Content-Type": "application/json"}
        return {"status": "FAILED", "message": "Password is not accepted"}, 400, {"Content-Type": "application/json"}

    @jwt_required
    @admin_required
    def put(self, id=None):
        parser = reqparse.RequestParser()
        parser.add_argument("username", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        parser.add_argument("status", type=bool, location="json", required=True)
        args = parser.parse_args()
        if id is not None:
            qry = Users.query.get(id)
            if qry is not None:
                validation = self.policy.test(args["password"])
                if validation == []:
                    pwd_digest = hashlib.md5(args["password"].encode()).hexdigest()
                    if Users.query.get(id).username != args["username"]:
                        if Users.query.filter_by(username=args["username"]).first() is not None:
                            return {"status": "FAILED", "message": "Username already exists"}, 400, {"Content-Type": "application/json"}
                    qry.username = args["username"]
                    qry.password = pwd_digest
                    qry.status = args["status"]
                    qry.updated_at = datetime.now()
                    db.session.commit()
                    return marshal(qry, Users.response_fields), 200, {"Content-Type": "application/json"}
                return {"status": "FAILED", "message": "Password is not accepted"}, 400, {"Content-Type": "application/json"}
        return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}

    @jwt_required
    @admin_required
    def delete(self, id=None):
        if id is not None:
            qry = Users.query.get(id)
            if qry is not None:
                qry.status = False
                db.session.commit()
                return {"message": "Succesfully deleted"}, 200, {"Content-Type": "application/json"}
        return {"message": "ID is not found"}, 404, {"Content-Type": "application/json"}



class UserResources(Resource):
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
        parser.add_argument("username", location="json", required=True)
        parser.add_argument("password", location="json", required=True)
        args = parser.parse_args()
        user_claims_data = get_jwt_claims()
        qry = Users.query.get(user_claims_data["id"])
        validation = self.policy.test(args["password"])
        if validation == []:
            pwd_digest = hashlib.md5(args["password"].encode()).hexdigest()
            if Users.query.get(user_claims_data["id"]).username != args["username"]:
                if Users.query.filter_by(username=args["username"]).first() is not None:
                    return {"status": "FAILED", "message": "Username already exists"}, 400, {"Content-Type": "application/json"}
            qry.username = args["username"]
            qry.password = pwd_digest
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


api_admin.add_resource(AdminResources, "", "/<int:id>")
api_user.add_resource(UserResources, "")