from flask import Flask, request, jsonify, render_template,  flash, request, redirect, url_for
from datetime import datetime, timedelta
import time
import urllib
import json
import sys
import os
import getopt
import argparse
import requests
import geocoder

today = datetime.now()

today_As_str = datetime.strftime(today, '%Y-%m-%d')
nextweek_As_str = datetime.strftime(today + timedelta(days=1), '%Y-%m-%d')

API_URL = "https://api.nasa.gov/planetary/apod"
NO_URL = "https://api.nasa.gov/neo/rest/v1/feed"
API_PARAMS = '?api_key={}&date={}'
NO_PARAMS = '?start_date={}&end_date={}&api_key={}'

nasa_api_key = 'RJIeNPaWJj0mYqhSc9Qh3iRpkc4FolE4vjfbPZup'

# https://api.nasa.gov/DONKI/GST?startDate=yyyy-MM-dd&endDate=yyyy-MM-dd&api_key=DEMO_KEY

# Init app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Home route
@app.route('/', methods=['GET'])
def home():

    g = geocoder.ip('me')
    location = g.latlng

    api_url = API_URL + API_PARAMS.format(nasa_api_key, today_As_str)
    response = urllib.urlopen(api_url)
    json_data = response.read()
    python_obj = json.loads(json_data)
    image_url = python_obj["url"]

    no_url = NO_URL + NO_PARAMS.format(today_As_str, today_As_str, nasa_api_key)
    no_response = requests.get(no_url)
    no_response.raise_for_status()
    no_data = json.loads(no_response.text)
    number_of_no = no_data["element_count"]
    neo = no_data["near_earth_objects"]
    nd = neo[today_As_str]
    neo_range = range(number_of_no)

    for n in neo_range:
        if nd[n]['is_potentially_hazardous_asteroid'] == True:
            data = nd[n]

    return render_template('home.html', image_url=image_url, location=location, data=data)

# Updates the css when changes are made
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

#Run server
if __name__ == '__main__':
    app.run(debug=True)
