import json, logging
from . import reset_db, user
from password_strength import PasswordPolicy

class TestProductList:
    def test_product_list(self, user):
        reset_db()
        