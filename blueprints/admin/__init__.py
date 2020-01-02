from flask_restful import Api
from flask import Blueprint

blueprint_admin = Blueprint("admin", __name__)
api_admin = Api(blueprint_admin)