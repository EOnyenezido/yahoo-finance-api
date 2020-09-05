from flask import Flask

app = Flask(__name__)

@app.errorhandler(404)
def route_not_found(error):
    return {
        "success": False,
        "message": "URL does not exist. Please use /stock/v1/get-price?region=__region__&symbol=__symbol__"
    }, 404