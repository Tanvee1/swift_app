import unittest
from app import create_app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_home_page(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Smart Shopping, Reimagined", res.data)

    def test_products_api(self):
        res = self.client.get('/api/products')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("products", data)
        self.assertTrue(len(data["products"]) >= 20)

    def test_chat_api(self):
        res = self.client.post('/api/chat', json={"message": "Where is Dettol?"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("reply", data)
        self.assertTrue(len(data["products"]) > 0)
        self.assertEqual(data["products"][0]["name"], "Dettol Handwash")

    def test_cart_calculation_api(self):
        cart_payload = {
            "items": [
                {"name": "Dettol Handwash", "price": 99.0, "quantity": 2},
                {"name": "Parle-G Biscuits", "price": 10.0, "quantity": 5}
            ]
        }
        res = self.client.post('/api/cart/calculate', json=cart_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["subtotal"], 248.0)
        self.assertEqual(data["tax"], 12.4)
        self.assertEqual(data["grand_total"], 300.4)

if __name__ == "__main__":
    unittest.main()
