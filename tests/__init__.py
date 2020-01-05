import pytest, logging, hashlib, json
from flask import Flask, request
from app import cache
from blueprints import app, db
from blueprints.user.model import Users
from blueprints.produk.model import Products, Specifications, Reviews
from blueprints.transaction.model import Transactions, Carts, ShipmentMethods, PaymentMethods


def call_user(request):
    user = app.test_client()
    return user

def reset_db():
    db.drop_all()
    db.create_all()
    # db user init
    user1 = Users("Adi", "Satu", "adi@robotaku.id", hashlib.md5("W@wew123".encode()).hexdigest())
    user2 = Users("Budi", "Dua", "budi@robotaku.id", hashlib.md5("W@wew123".encode()).hexdigest())
    user3 = Users("Cici", "Tiga", "cici@robotaku.id", hashlib.md5("W@wew123".encode()).hexdigest())
    user4 = Users("Dodi", "Empat", "dodi@robotaku.id", hashlib.md5("W@wew123".encode()).hexdigest())
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.commit()

    # db product init
    product1 = Products("DC Motor", 90000, "Aktuator & Power System", "Aktuator cocok untuk RC Car")
    product2 = Products("Basher SaberTooth 1/8 Scale", 3200000, "UGV / RC Car", "RC Car dari Basher!")
    product3 = Products("6-DOF Arm Robot Mechanical Frame", 2100000, "Robotik & Kit", "Serial manipulator terbaru!")
    product4 = Products("Stepper Motor", 15000, "Aktuator & Power System", "Aktuator cocok untuk position control")
    db.session.add(product1)
    db.session.add(product2)
    db.session.add(product3)
    db.session.add(product4)
    db.session.commit()

    # db spec product1 init
    spec1 = Specifications(1, "Power rating: 24 VDC")
    spec2 = Specifications(1, "Maximum speed: 5000 rpm")
    db.session.add(spec1)
    db.session.add(spec2)
    # db spec product2 init
    spec3 = Specifications(2, "ESC: 100A w/ Reverse Waterproof (HXT4mm Connectors)")
    spec4 = Specifications(2, "Motor:  3674 Inrunner 1845Kv")
    db.session.add(spec3)
    db.session.add(spec4)
    # db spec product3 init
    spec5 = Specifications(3, "Power rating: 12 VDC")
    spec6 = Specifications(3, "Material: Metal alloy")
    db.session.add(spec5)
    db.session.add(spec6)
    # db spec product4 init
    spec7 = Specifications(4, "Power rating: 6 VDC")
    spec8 = Specifications(4, "Resolution: 200 steps/rev")
    db.session.add(spec7)
    db.session.add(spec8)
    db.session.commit()

    # db payment method init
    payment1 = PaymentMethods("BINI", "048918272018", 100)
    payment2 = PaymentMethods("BACA", "098918238618", 300)
    payment3 = PaymentMethods("MANDORI", "028210272018", 200)
    db.session.add(payment1)
    db.session.add(payment2)
    db.session.add(payment3)
    db.session.commit()
    
    # db shipment method init    
    shipment1 = ShipmentMethods("JENI Yosh", 18000)
    shipment2 = ShipmentMethods("SangKodok Sehari", 15000)
    shipment3 = ShipmentMethods("Wahaha Reguler", 7000)
    db.session.add(shipment1)
    db.session.add(shipment2)
    db.session.add(shipment3)
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