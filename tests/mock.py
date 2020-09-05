error_message = "This is a sample exception message from the mock"

success_response_sample = {
    "price": {
        "currency": "USD", 
        "currencySymbol": "$", 
        "exchangeName": "NasdaqGM",
        "regularMarketPrice": { 
            "raw": 4.3, 
            "fmt": "4.3000",
        }, 
        "longName": "Amarin Corporation plc",
        "regularMarketTime": 1599249601
  }
}

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code, headers, error, error_message):
            self.json_data = json_data
            self.status_code = status_code
            self.headers = headers
            self.error = error
            self.error_message = error_message

        def __iter__(self):
            for attr in dir(self):
                if not attr.startswith("__"):
                    yield attr

        def __getitem__(self, item):
            data = {
                "error": self.error,
                "error_message": self.error_message
            }
            return data[item]

        def json(self):
            return self.json_data

        def raise_for_status(self):
            pass
    
    if kwargs["params"]["region"] == "US" and kwargs["params"]["symbol"] == "AMRN":
        return MockResponse(success_response_sample, 200, {"content-length": "3490"}, False, "")
    elif kwargs["params"]["symbol"] == "error":
        return MockResponse({}, 500, {"content-length": "3490"}, True, error_message)
    elif kwargs["params"]["symbol"] == "****":
        return MockResponse({}, 200, {"content-length": "0"}, False, "")
    elif kwargs["params"]["symbol"] == "no_raw_price":
        return MockResponse({}, 200, {"content-length": "3490"}, False, "")

    return MockResponse({}, 404, {"content-length": "0"}, False, "")