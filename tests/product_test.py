import json, logging
from . import reset_db, user
from password_strength import PasswordPolicy

class TestProductList:
    def test_all_product_list(self, user):
        reset_db()
        data = {}
        res = user.get("/api/product", query_string=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_all_product_filtered_keyword(self, user):
        reset_db()
        data = {"keyword": "robot"}
        res = user.get("/api/product", query_string=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_all_product_filtered_kategori(self, user):
        reset_db()
        data = {"kategori": "UGV / RC Car"}
        res = user.get("/api/product", query_string=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_all_product_filtered_page(self, user):
        reset_db()
        data = {"p":2, "rp": 4}
        res = user.get("/api/product", query_string=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_all_product_filtered_rating(self, user):
        reset_db()
        data = {"rating": 0}
        res = user.get("/api/product", query_string=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200
    
    def test_show_product_by_id_not_found(self, user):
        reset_db()
        data = {}
        res = user.get("/api/product/5", query_string=data)
        res_json = json.loads(res.data)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 404
    
    def test_show_product_by_id(self, user):
        reset_db()
        data = {}
        res = user.get("/api/product/1", query_string=data)
        res_json = json.loads(res.data)
        print(res_json)
        logging.warning("RESULT: %s", res_json)
        assert res.status_code == 200