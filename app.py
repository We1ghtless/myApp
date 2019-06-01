from flask import Flask, request, jsonify, render_template,  flash, request, redirect, url_for
from datetime import datetime, timedelta
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FileField, IntegerField
import time
import urllib
import json
import sys
import os
import getopt
import argparse
import requests
import geocoder
import pythonUntappd
import babel

app = Flask(__name__)

today = datetime.now()

today_As_str = datetime.strftime(today, '%Y-%m-%d')
nextweek_As_str = datetime.strftime(today + timedelta(days=1), '%Y-%m-%d')

API_URL = "https://api.untappd.com/v4"
TRENDING = "https://api.untappd.com/v4/beer/trending"
BID = "https://api.untappd.com/v4/beer/info/{}"
BREWERY = "https://api.untappd.com/v4/brewery/info/{}"
CHECKINS = "https://api.untappd.com/v4/beer/checkins/{}"
CLIENT_ID = "A3F72945ACFCA109BFC672EF1FA58A679AAB238B"
CLIENT_SECRET = "B02EF4FC7AA1F189ED2CDE9E91D86C536828EFA0"
API_PARAMS = "?client_id={}&client_secret={}"
REDIRECT_URL = "localhost:5000"

api = pythonUntappd.api(CLIENT_ID, CLIENT_SECRET)

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():

    form = SearchForm(request.form)

    api_url = TRENDING + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)

    trending_response = urllib.urlopen(api_url)
    json_data = trending_response.read()
    data = json.loads(json_data)

    beers = data['response']['macro']['items']

    if request.method == 'POST' and form.validate():

        input = str(form.search.data)

        return redirect(url_for('search', input=input))

    else:

        return render_template('home.html', form=form, beers=beers)


@app.route('/search/<string:input>', methods=['GET', 'POST'])
def search(input):

    form = SearchForm(request.form)

    response = api.beer_search('{}'.format(input))

    data = response['response']

    items = data['beers']

    beers = items['items']

    if request.method == 'POST' and form.validate():

        input = str(form.search.data)

        return redirect(url_for('search', input=input))

    else:

        return render_template('search.html', beers=beers, form=form)

@app.route('/beer/<string:bid>')
def beer(bid):

    api_url = BID.format(bid) + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)

    response = urllib.urlopen(api_url)
    json_data = response.read()
    data = json.loads(json_data)

    beer = data['response']['beer']
    brewery = data['response']['beer']['brewery']

    info = data['response']['beer']['media']['items']

    # for n in info:
    #     for venue in n['venue']:
    #         for i in venue:

    api_url = CHECKINS.format(bid) + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)

    response = urllib.urlopen(api_url)
    json_data = response.read()
    data = json.loads(json_data)

    checkins = data['response']['checkins']['items']

    return render_template('beer.html', info=info, beer=beer, brewery=brewery, checkins=checkins)

@app.route('/brewery/<string:breweryid>')
def brewery(breweryid):

    api_url = BREWERY.format(breweryid) + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)

    response = urllib.urlopen(api_url)
    json_data = response.read()
    data = json.loads(json_data)

    brewery = data['response']
    checkins = brewery['brewery']['media']['items']

    return render_template('brewery.html', brewery=brewery, checkins=checkins)

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

class SearchForm(Form):
    search = StringField('search', [validators.length(min=1)], render_kw={"placeholder": "Search beers"})

#Run server
if __name__ == '__main__':
    app.run(debug=True)
