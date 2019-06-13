from flask import Flask, request, jsonify, render_template, redirect, url_for
from wtforms import Form, StringField, validators
import time
import urllib
import json
import sys
import os
import requests
import pythonUntappd


app = Flask(__name__)

#Urls for making api requests
API_URL = "https://api.untappd.com/v4"
TRENDING = "https://api.untappd.com/v4/beer/trending"
LOCAL = "https://api.untappd.com/v4/thepub/local"
BID = "https://api.untappd.com/v4/beer/info/{}"
BREWERY = "https://api.untappd.com/v4/brewery/info/{}"
CHECKINS = "https://api.untappd.com/v4/beer/checkins/{}"
VENUE = "https://api.untappd.com/v4/venue/info/{}"
CLIENT_ID = "A3F72945ACFCA109BFC672EF1FA58A679AAB238B"
CLIENT_SECRET = "B02EF4FC7AA1F189ED2CDE9E91D86C536828EFA0"
API_PARAMS = "?client_id={}&client_secret={}"
REDIRECT_URL = "localhost:5000"

api = pythonUntappd.api(CLIENT_ID, CLIENT_SECRET)

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():

    #create instance of the form class in def
    form = SearchForm(request.form)

    #url request to get a json response
    api_url = TRENDING + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)
    trending_response = urllib.urlopen(api_url)
    json_data = trending_response.read()
    data = json.loads(json_data)

    #stepping through the json
    beers = data['response']['macro']['items']

    #if statement to see if the search bar has been used
    if request.method == 'POST' and form.validate():

        input = str(form.search.data)

        #if it has redirect to the search page
        return redirect(url_for('search', input=input, form=form))

    else:

        return render_template('home.html', form=form, beers=beers)

#search route
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

        return render_template('search.html', beers=beers, form=form, input=input)

#route for beer by id
@app.route('/beer/<string:bid>', methods=['GET', 'POST'])
def beer(bid):

    form = SearchForm(request.form)

    api_url = BID.format(bid) + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)

    response = urllib.urlopen(api_url)
    json_data = response.read()
    data = json.loads(json_data)

    beer = data['response']['beer']
    brewery = data['response']['beer']['brewery']

    info = data['response']['beer']['media']['items']

    api_url = CHECKINS.format(bid) + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)

    response = urllib.urlopen(api_url)
    json_data = response.read()
    data = json.loads(json_data)

    checkins = data['response']['checkins']['items']

    if request.method == 'POST' and form.validate():

        input = str(form.search.data)

        return redirect(url_for('search', input=input))

    return render_template('beer.html', info=info, beer=beer, brewery=brewery, checkins=checkins, form=form)

@app.route('/brewery/<string:breweryid>', methods=['GET', 'POST'])
def brewery(breweryid):

    form = SearchForm(request.form)

    api_url = BREWERY.format(breweryid) + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)

    response = urllib.urlopen(api_url)
    json_data = response.read()
    data = json.loads(json_data)

    brewery = data['response']
    checkins = brewery['brewery']['media']['items']

    if request.method == 'POST' and form.validate():

        input = str(form.search.data)

        return redirect(url_for('search', input=input))

    return render_template('brewery.html', brewery=brewery, checkins=checkins, form=form)

@app.route('/venue/<string:venueid>', methods=['GET', 'POST'])
def venue(venueid):

    form = SearchForm(request.form)

    api_url = VENUE.format(venueid) + API_PARAMS.format(CLIENT_ID, CLIENT_SECRET)

    response = urllib.urlopen(api_url)
    json_data = response.read()
    data = json.loads(json_data)

    venue = data['response']
    checkins = venue['venue']['media']['items']
    popular = venue['venue']['top_beers']['items']

    if request.method == 'POST' and form.validate():

        input = str(form.search.data)

        return redirect(url_for('search', input=input))

    return render_template('venue.html', venue=venue, checkins=checkins, popular=popular, form=form)

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

#form class for the search element using wtformss
class SearchForm(Form):
    search = StringField('', [validators.length(min=1)], render_kw={"placeholder": "Search beers"})

#Run server
if __name__ == '__main__':
    app.run(debug=True)
