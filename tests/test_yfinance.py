import unittest

from yfinance import app # pylint: disable=F0401

class TestYFinance(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_response_is_always_json(self):
        """
        GIVEN any url
        WHEN a request is mad
        THEN should return a JSON response
        """
        rv = self.client.get("/")
        self.assertTrue(rv.is_json)
        rv = self.client.get("/stock/v1/get-price?region=US&symbol=****")
        self.assertTrue(rv.is_json)
        rv = self.client.get("/stock/v1/get-price?region=US&symbol=AMRN")
        self.assertTrue(rv.is_json)

    def test_route_not_found_error_code(self):
        """
        GIVEN a wrong url
        WHEN a request is made
        THEN should return a 404 error code
        """
        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 404)
        self.assertTrue(rv.is_json)

    def test_url_not_found_error_message(self):
        """
        GIVEN a wrong url
        WHEN a request is made
        THEN should return an appropriate error message
        """
        rv = self.client.get("/")
        self.assertTrue(rv.is_json)
        body = rv.get_json()
        self.assertEqual(body["success"], False)
        self.assertIn("URL does not exist", body["message"])