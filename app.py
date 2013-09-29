from __future__ import division
from flask import Flask, request, render_template, json, url_for, redirect, session
import urllib, urllib2, os, urlparse, time
from random import randint
from parse_rest.connection import register, ParseBatcher
from parse_rest.datatypes import Object
from parse_rest.query import QueryResourceDoesNotExist

# parse for dev purposes
register('jWkR2kmHwh45o14jXDmoA9ujE7T5LVGfLPnaWwN0', '3yENrtbiaiu3k934sehtjq8VMNiTrzZo6Za8J5ob')

app = Flask(__name__)

app = Flask(__name__)
app.secret_key = 'some_random_secret'

INSTAGRAM_CLIENT_ID = 'd18a0312ac06430cba43f02ccbf9c5d4'
INSTAGRAM_CLIENT_SECRET = '7a2040afd3044962a636ac001be5f5a2'

REDIRECT_URI_DEV = 'http://127.0.0.1:5000/igram_oauth_callback'
REDIRECT_URI_PROD = 'http://desolate-woodland-8107.herokuapp.com/igram_oauth_callback'
GRANT_TYPE = 'authorization_code'

app.secret_key = 'some_random_secret'

# Elo Rating System constants
BASE_RATING = 1400
KC = 32
WIN = 1
LOSS = 0

class Photo(Object):
    pass


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/igram_oauth_callback')
def igram_oauth():
    if 'code' in request.args:
        session['code'] = request.args.get('code')

    return redirect(url_for('logged_in'))


@app.route('/welcome')
def logged_in():
    if 'user' not in session:
        endpoint = 'https://api.instagram.com/oauth/access_token'
        values = {'client_id': INSTAGRAM_CLIENT_ID,
                  'client_secret': INSTAGRAM_CLIENT_SECRET,
                  'grant_type': GRANT_TYPE,
                  'redirect_uri': REDIRECT_URI_PROD,
                  'code': session['code'] }

        data = urllib.urlencode(values)
        req = urllib2.Request(endpoint, data)
        resp = urllib2.urlopen(req)
        resp_json = json.loads(resp.read())

        user = {}

        user['token'] = resp_json['access_token']
        user['username'] = resp_json['user']['username']
        user['user_id'] = resp_json['user']['id']
        session['user'] = user

    return render_template('join.html', user=session['user'])


@app.route("/tally_round", methods=['POST'])
def tally_round():
    photo1_raw = None
    photo2_raw = None
    result = None
    if 'photo1' in request.form and 'photo2' in request.form and 'result' in request.form:
        photo1_raw = request.form['photo1']
        photo2_raw = request.form['photo2']
        result = request.form['result']
        # validate POST data for security
        photo1_url = urlparse.urlparse(photo1_raw)
        photo2_url = urlparse.urlparse(photo2_raw)
        if photo1_url.scheme != 'http' or photo1_url.query != '' or photo1_url.params != '':
            return json.dumps({"errorMsg": "Invalid data"}), 400
        if photo2_url.scheme != 'http' or photo2_url.query != '' or photo2_url.params != '':
            return json.dumps({"errorMsg": "Invalid data"}), 400
        if result != 'win' and result != 'loss':
            return json.dumps({"errorMsg": "Invalid data"}), 400
    else:
        return json.dumps({"errorMsg": "Invalid data"}), 400


    print photo1_raw, photo2_raw, result
    try:
        photo1 = Photo.Query.get(img_url=photo1_raw)
        photo2 = Photo.Query.get(img_url=photo2_raw)
    except QueryResourceDoesNotExist:
        return json.dumps({"errorMsg": "Invalid data"}), 400

    ratings = updateRating(photo1, photo2, result)
    photo1.rating = ratings[0]
    photo2.rating = ratings[1]

    photos = [photo1, photo2]
    try:
        batcher = ParseBatcher()
        batcher.batch_save(photos)
    except:
        print "ERROR failed to save vote!"

    return json.dumps({"success": True}), 200


def updateRating(photo1, photo2, result):
    pl_one = photo1.rating
    pl_two = photo2.rating

    eA = 1 / (1 + 10**((pl_two - pl_one)/400))
    eB = 1 / (1 + 10**((pl_one - pl_two)/400))
    print "expected: ", eA, eB
    if result == 'win':
        pl_one = pl_one + KC*(WIN - eA)
        pl_two = pl_two + KC*(LOSS - eB)
        print "pl_one: ", pl_one
        print "pl_two: ", pl_two
    if result == 'loss':
        pl_one = pl_one + KC*(LOSS - eA)
        pl_two = pl_two + KC*(WIN - eB)
        print "pl_one: ", pl_one
        print "pl_two: ", pl_two

    return [pl_one, pl_two]


@app.route("/new_round")
def new_round():
    players = get_new_players()

    print "players: ", players[0].img_url, players[1].img_url
    return json.dumps([players[0].img_url, players[1].img_url])


""" Returns a list containing two new players
"""
def get_new_players():
    all = Photo.Query.all()
    count = all.count()
    rand1 = randint(0, count - 1)
    rand2 = randint(0, count - 1)
    while rand1 == rand2:
        rand2 = randint(0, count - 1)
    qs1 = all.limit(1).skip(rand1)
    qs2 = all.limit(1).skip(rand2)
    players = []
    for item in qs1:
        players.append(item)

    for item in qs2:
        players.append(item)

    return players


@app.route("/rating")
def rating():
    photo_urls = ['http://distilleryimage5.s3.amazonaws.com/8ba48b0a283c11e3aa8c22000a1fc809_7.jpg',
                  'http://distilleryimage7.s3.amazonaws.com/5ecb6cf028b611e3b16122000a1f9e61_7.jpg',
                  'http://distilleryimage2.s3.amazonaws.com/fa569a4828b411e3948222000a1f9307_8.jpg',
                  'http://distilleryimage3.s3.amazonaws.com/e172b9ac28b511e3ab9022000a9f14bb_7.jpg',
                  'http://distilleryimage5.s3.amazonaws.com/27bfdfde28b611e387d622000aeb0b75_7.jpg',
                  'http://distilleryimage8.s3.amazonaws.com/0ffe132828b311e3ab3e22000a1fb352_7.jpg',
                  'http://distilleryimage3.s3.amazonaws.com/2217cbd228b611e3a0fd22000aa8039a_8.jpg',
                  'http://distilleryimage4.s3.amazonaws.com/5367aa4a28b611e3a1ff22000a1fcee4_7.jpg',
                  'http://distilleryimage10.s3.amazonaws.com/278be1ac28b611e3872722000a1fd26f_7.jpg',
                  'http://distilleryimage1.s3.amazonaws.com/5b488e54285311e3b30422000aaa0585_7.jpg']


    for url in photo_urls:
        try:
            aPhoto = Photo.Query.get(img_url=url)
        except:
            aPhoto = Photo(img_url=url, rating=BASE_RATING)
            aPhoto.save()

    return render_template('ratingtest.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
