import pytest, logging, hashlib, json
from flask import Flask, request
from app import cache
from blueprints import app, db
from blueprints.user.model import Users


def call_user(request):
    user = app.test_client()
    return user

def reset_db():
    db.drop_all()
    db.create_all()
    user1 = Users("Adi", "Satu", "adi@robotaku.id", hashlib.md5("W@wew123".encode()).hexdigest())
    user2 = Users("Budi", "Dua", "budi@robotaku.id", hashlib.md5("W@wew123".encode()).hexdigest())
    user3 = Users("Cici", "Tiga", "cici@robotaku.id", hashlib.md5("W@wew123".encode()).hexdigest())
    user4 = Users("Dodi", "Empat", "dodi@robotaku.id", hashlib.md5("W@wew123".encode()).hexdigest())
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.commit()


@pytest.fixture
def user(request):
    return call_user(request)

def create_token(is_admin=True):
    if is_admin: cache_user = "test_token_admin"
    else: cache_user = "test_token_nonadmin"
    token = cache.get(cache_user)
    if token is None:
        # prepare request input
        if is_admin:
            data = {
                "email": "admin@robotaku.id",
                "password": "W@wew123"
            }
        else:
            data = {
                "email": "adi@robotaku.id",
                "password": "W@wew123"
            }
        # do request
        req = call_user(request)
        res = req.get("/auth", json=data)
        # store response
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        # compare with expected result
        assert res.status_code == 200
        assert res_json["message"] == "Token is successfully created"
        # save token into cache
        cache.set(cache_user, res_json["token"], timeout=30)
        # return
        return res_json["token"]
    return token