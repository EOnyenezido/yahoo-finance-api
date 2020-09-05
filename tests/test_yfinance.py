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

    @patch('yfinance.requests.get', side_effect=mocked_requests_get)
    def test_yahoo_finance_api_empty_data_response(self, mock_get):
        """
        GIVEN yahoo finance returns a response with empty data
        THEN should return 412 error with an error message
        """
        rv = self.client.get("/stock/v1/get-price?region=US&symbol=****") # mock empty data endpoint
        self.assertTrue(rv.is_json)
        self.assertEqual(rv.status_code, 412)
        body = rv.get_json()
        self.assertEqual(body["success"], False)
        self.assertEqual(body["message"], "No data found. Please re-confirm instrument symbol")

    @patch('yfinance.requests.get', side_effect=mocked_requests_get)
    def test_yahoo_finance_api_no_raw_price_in_response(self, mock_get):
        """
        GIVEN yahoo finance returns a response without raw price
        *** this is rare, but happens because the API has a 93% success rate
        THEN should return 503 error with an error message
        """
        rv = self.client.get("/stock/v1/get-price?region=US&symbol=no_raw_price") # mock no raw price endpoint
        self.assertTrue(rv.is_json)
        self.assertEqual(rv.status_code, 503)
        body = rv.get_json()
        self.assertEqual(body["success"], False)
        self.assertEqual(body["message"], "Retrieving price from API failed. Please retry")

    @patch('yfinance.requests.get', side_effect=mocked_requests_get)
    def test_yahoo_finance_api_success_response(self, mock_get):
        """
        GIVEN yahoo finance returns a successful response with required information
        THEN should return 200 with all the required information
        """
        rv = self.client.get("/stock/v1/get-price?region=US&symbol=AMRN") # mock no raw price endpoint
        self.assertTrue(rv.is_json)
        self.assertEqual(rv.status_code, 200)
        body = rv.get_json()
        self.assertEqual(body["success"], True)
        self.assertEqual(body["message"], "Price obtained successfully")
        expected_response = {
            "currency": "USD", 
            "currencySymbol": "$", 
            "exchangeName": "NasdaqGM", 
            "fmt": "4.3000", 
            "name": "Amarin Corporation plc", 
            "raw": 4.3, 
            "regularMarketTime": 1599249601
        }
        self.assertEqual(body["price"], expected_response)

if __name__ == '__main__':
    unittest.main()