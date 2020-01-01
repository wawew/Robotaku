from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import db, admin_required, nonadmin_required, app
from sqlalchemy import desc
from password_strength import PasswordPolicy
from datetime import datetime
from .model import Watchlists
import requests

blueprint_watchlist = Blueprint('watchlist', __name__)
api = Api(blueprint_watchlist)

class WatchlistsResources(Resource):
    host = 'https://api.themoviedb.org/3'
    api_key = 'df1a34ae3c1705433378bc967b244227'

    @jwt_required
    @nonadmin_required
    def get(self):
        parser =reqparse.RequestParser()
        parser.add_argument("p", type=int, location="args", default=1)
        parser.add_argument("rp", type=int, location="args", default=5)
        parser.add_argument('genre', location='args', default=None)
        args = parser.parse_args()

        claims = get_jwt_claims()
        data = Watchlists.query.filter_by(user_id=claims['id'])
        # print(data.all())
        movies = []
        for qry in data.all():

            rq = requests.get(self.host + '/movie/' + str(qry.movie_id), params={
                'api_key':self.api_key,
                })
            movie = rq.json()

            nama_genre=[]
            genre = movie['genres']
            for i in genre:
                nama_genre.append(i['name'])

            hasil = {
                'movie_id': movie['id'],
                'judul': movie['title'],
                'sinopsis': movie['overview'],
                'genres': nama_genre,
                'tanggal_rilis': movie['release_date'],
                'status_rilis': movie['status'],
                'durasi': movie['runtime'],
                'rating': movie['vote_average']
            }
            if args['genre'] is not None:
                if args['genre'] in hasil['genres']:
                    movies.append(hasil)
            else:
                movies.append(hasil)

        return movies, 200

    @jwt_required
    @nonadmin_required
    def post(self):
        parser =reqparse.RequestParser()
        parser.add_argument("movie_id", type=int, location="args")
        args = parser.parse_args()

        claims = get_jwt_claims()
        user_id = claims['id']
        data = Watchlists.query.filter_by(user_id=user_id)
        data = data.filter_by(movie_id=args['movie_id']).first()

        if data is not None:
            return {'message':'movie already added in watchlist'}, 400
        else:
            watch = Watchlists(user_id, args['movie_id'])
            db.session.add(watch)
            db.session.commit()
            app.logger.debug('DEBUG : %s', watch)

            return {'status':'Success'}, 200

    @jwt_required
    @nonadmin_required
    def delete(self):
        parser =reqparse.RequestParser()
        parser.add_argument("movie_id", type=int, location="args")
        args = parser.parse_args()

        claims = get_jwt_claims()
        user_id = claims['id']
        data = Watchlists.query.filter_by(user_id = user_id)
        qry = data.filter_by(movie_id = args['movie_id']).first()

        if qry is None:
            return {'status':'NOT_FOUND'}, 404

        #hard delete
        db.session.delete(qry)
        db.session.commit()
        return 'Deleted', 200

api.add_resource(WatchlistsResources, "", "/<int:id>")
