import json, logging
from . import reset_db, user
from password_strength import PasswordPolicy

class TestAuth:
    # GET METHOD
    def test_invalid_user(self, user):
        reset_db()
        data = {"email": "wawawaw", "password": "W@wew123"}
        res = user.put("/api/auth", json=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 401
        assert res_json["status"] == "UNAUTHORIZED"
        assert res_json["message"] == "Invalid email or password"
    
    # POST METHOD
    def test_create_user_success(self, user):
        reset_db()
        data = {
            "nama_depan":"Eni", "nama_belakang":"Lima",
            "email":"eni@robotaku.id", "password":"W@wew123"
        }
        res = user.post("/api/auth", json=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_create_user_email_already_exists(self, user):
        reset_db()
        data = {
            "nama_depan":"Eni", "nama_belakang":"Lima",
            "email":"adi@robotaku.id", "password":"W@wew123"
        }
        res = user.post("/api/auth", json=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 400
        assert res_json["status"] == "FAILED"
        assert res_json["message"] == "Email already exists"
    
    def test_create_user_password_not_valid(self, user):
        reset_db()
        data = {
            "nama_depan":"Eni", "nama_belakang":"Lima",
            "email":"adi@robotaku.id", "password":"Wawew123"
        }
        res = user.post("/api/auth", json=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 400
        assert res_json["status"] == "FAILED"
        assert res_json["message"] == "Password is not accepted"