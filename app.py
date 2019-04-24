from flask import Flask, request, jsonify, render_template,  flash, request, redirect, url_for
from datetime import datetime
import time
import urllib
import json
import sys
import os
import getopt
import argparse

today = datetime.now()

today_As_str = datetime.strftime(today, '%Y-%m-%d')

API_URL = "https://api.nasa.gov/planetary/apod"
API_PARAMS = '?api_key={}&date={}'

api_key = 'RJIeNPaWJj0mYqhSc9Qh3iRpkc4FolE4vjfbPZup'

#Init app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():

    api_url = API_URL + API_PARAMS.format(api_key, today_As_str)

    response = urllib.urlopen(api_url)

    json_data = response.read()

    python_obj = json.loads(json_data)

    image_url = python_obj["url"]

    return render_template('home.html', image_url=image_url)

#Run server
if __name__ == '__main__':
    app.run(debug=True)
