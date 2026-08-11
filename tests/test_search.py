import unittest
from backend.services.search_service import SearchService

class TestSearchService(unittest.TestCase):
    def setUp(self):
        self.search_service = SearchService()

    def test_exact_name_match(self):
        products, s_filter = self.search_service.search("Dettol Handwash")
        self.assertTrue(len(products) > 0)
        self.assertEqual(products[0].name, "Dettol Handwash")

    def test_price_constraint_query(self):
        products, s_filter = self.search_service.search("Snacks under 50")
        self.assertEqual(s_filter.max_price, 50.0)
        for p in products:
            self.assertTrue(p.price <= 50.0)

    def test_aisle_constraint_query(self):
        products, s_filter = self.search_service.search("Tell me item in aisle 2")
        self.assertEqual(s_filter.aisle, "aisle 2")
        for p in products:
            self.assertEqual(p.location.lower(), "aisle 2")

    def test_vector_semantic_search(self):
        products, s_filter = self.search_service.search("germ protection antibacterial liquid")
        self.assertTrue(len(products) > 0)
        self.assertTrue("Dettol" in products[0].name or "Handwash" in products[0].name)

if __name__ == "__main__":
    unittest.main()
