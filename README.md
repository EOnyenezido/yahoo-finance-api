# yahoo-finance-api
A python API that connects to "Yahoo Finance API Pricing" and returns a given instrument's pricing

![Unit Tests](https://github.com/EOnyenezido/yahoo-finance-api/workflows/Unit%20Tests/badge.svg?branch=master)

#### To quickly run application
1. pip install -r requirements.txt
1. export FLASK_APP=yfinance.py
1. flask run **(localhost only)**
1. flask run --host=0.0.0.0 **(externally visible server)**

#### To run unit tests
1. pip install -r requirements.txt
1. python -m unittest tests/test_yfinance.py

#### To view test coverage
1. pip install -r requirements.txt
1. coverage run tests/test_yfinance.py
1. coverage report yfinance.py **(command line report)**
1. coverage html yfinance.py **(view report as html page)**
