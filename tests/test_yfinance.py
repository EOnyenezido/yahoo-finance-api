import unittest
from unittest.mock import patch
from tests.mock import mocked_requests_get # pylint: disable=F0401

from yfinance import app # pylint: disable=F0401
from config import supportedRegions # pylint: disable=F0401

class TestYFinance(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('yfinance.requests.get', side_effect=mocked_requests_get)
    def test_response_is_always_json(self, mock_get):
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

    def test_region_must_be_in_request_url(self):
        """
        GIVEN a url without region paramater
        WHEN a request is made
        THEN should return bad request error
        """
        rv = self.client.get("/stock/v1/get-price?symbol=AMRN")
        self.assertTrue(rv.is_json)
        self.assertEqual(rv.status_code, 400)
        body = rv.get_json()
        self.assertEqual(body["success"], False)
        self.assertIn("Unsupported region", body["message"])

    def test_region_must_be_supported_region(self):
        """
        GIVEN a url with an unsupported region paramater
        WHEN a request is made
        THEN should return bad request error including a list of supported regions
        """
        rv = self.client.get("/stock/v1/get-price?region=**&symbol=AMRN")
        self.assertTrue(rv.is_json)
        self.assertEqual(rv.status_code, 400)
        body = rv.get_json()
        self.assertEqual(body["success"], False)
        self.assertEqual(body["message"], "Unsupported region. Please specify one of " + ",".join(supportedRegions))

    def test_symbol_must_be_in_request_url(self):
        """
        GIVEN a url without an instrument symbol paramater
        WHEN a request is made
        THEN should return bad request error
        """
        rv = self.client.get("/stock/v1/get-price?region=US")
        self.assertTrue(rv.is_json)
        self.assertEqual(rv.status_code, 400)
        body = rv.get_json()
        self.assertEqual(body["success"], False)
        self.assertEqual("Please pass instrument symbol", body["message"])

    @patch('yfinance.requests.get', side_effect=mocked_requests_get)
    def test_yahoo_finance_api_connection_error(self, mock_get):
        """
        GIVEN app is unable to connect to Yahoo Finance API
        WHEN a request is made
        THEN should return 500 error with an error message
        """
        rv = self.client.get("/stock/v1/get-price?region=US&symbol=error") # mock error endpoint
        self.assertTrue(rv.is_json)
        self.assertEqual(rv.status_code, 500)
        body = rv.get_json()
        self.assertEqual(body["success"], False)
        self.assertEqual(body["message"], "An error occurred while connecting to the API. See 'error_message' for reason")
        self.assertEqual(body["error_message"], "This is a sample exception message from the mock")