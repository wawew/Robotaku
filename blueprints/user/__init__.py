from flask_restful import Api
from flask import Blueprint

blueprint_user = Blueprint("user", __name__)
api_user = Api(blueprint_user)