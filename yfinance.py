import requests

from flask import Flask, request
from config import supportedRegions, url, rapidapi_host, rapidapi_key

app = Flask(__name__)

@app.route('/stock/v1/get-price')
def get_price():
    # validate that a supported region is in the request url
    region = request.args.get('region', '').upper()
    if region not in supportedRegions:
        return {
            "success": False,
            "message": "Unsupported region. Please specify one of " + ",".join(supportedRegions)
        }, 400
    
    # validate that the instrument symbol is in the request url
    symbol = request.args.get('symbol', '')
    if symbol == "":
        return {
            "success": False,
            "message": "Please pass instrument symbol"
        }, 400

    # get the data from the Yahoo Finance API
    data = get_api_data(region, symbol)

    # if unable to connect to the API for any reason, return the error reason
    if ("error" in data and data["error"]):
        return {
            "success": False,
            "message": "An error occurred while connecting to the API. See 'error_message' for reason",
            "error_message": data["error_message"]
        }, 500
    
    # If the instrument symbol returns no data
    # we make sure the user gets a 'precondition failed' error
    if data.headers["content-length"] == "0":
        return {
            "success": False,
            "message": "No data found. Please re-confirm instrument symbol"
        }, 412
    
    # Get the JSON
    data = data.json()

    # Yahoo Finance API has a 93% success rate
    # so we need make sure at least the raw price is always returned
    if "raw" not in data.get("price", {}).get("regularMarketPrice", {}):
        return {
            "success": False,
            "message": "Retrieving price from API failed. Please retry"
        }, 503

    # return final result
    return {
        "success": True,
        "message": "Price obtained successfully",
        "price": {
            "name": data.get("price", {}).get("longName", ""),
            "raw": data.get("price", {}).get("regularMarketPrice", {}).get("raw"), # must always be in response
            "fmt": data.get("price", {}).get("regularMarketPrice", {}).get("fmt", ""),
            "currency": data.get("price", {}).get("currency", ""),
            "currencySymbol": data.get("price", {}).get("currencySymbol", ""),
            "exchangeName": data.get("price", {}).get("exchangeName", ""),
            "regularMarketTime": data.get("price", {}).get("regularMarketTime", 0)
        }
    }

@app.errorhandler(404)
def route_not_found(error):
    return {
        "success": False,
        "message": "URL does not exist. Please use /stock/v1/get-price?region=__region__&symbol=__symbol__"
    }, 404

# function to use the requests library to call the Yahoo Finance API
def get_api_data(region, symbol):    

    querystring = {"region":region,"symbol":symbol}

    headers = {
        'x-rapidapi-host': rapidapi_host,
        'x-rapidapi-key': rapidapi_key
        }

    try:
        response = requests.get(url, params=querystring, headers=headers)
        response.raise_for_status() # 401 unauthorized, in case our API limit is reached
    except requests.exceptions.RequestException as e:
        response = {
            "error": True,
            "error_message": str(e)
        }    
    
    return response