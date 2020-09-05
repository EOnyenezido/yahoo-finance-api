from flask import Flask, request
from config import supportedRegions

app = Flask(__name__)

@app.route('/stock/v1/get-price')
def get_price():
    region = request.args.get('region', '').upper()
    if region not in supportedRegions:
        return {
            "success": False,
            "message": "Unsupported region. Please specify one of " + ",".join(supportedRegions)
        }, 400

    return {} # return an empty JSON until integration with Yahoo Finance API

@app.errorhandler(404)
def route_not_found(error):
    return {
        "success": False,
        "message": "URL does not exist. Please use /stock/v1/get-price?region=__region__&symbol=__symbol__"
    }, 404