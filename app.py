from __future__ import division
from flask import Flask, request, render_template, json, url_for, redirect, session
from parse import Media, Parse, Rating
from parse_rest.connection import ParseBatcher
from parse_rest.query import QueryResourceDoesNotExist
from random import randint
from rating import BASE_RATING, KC, WIN, LOSS

import ast, urllib, urllib2, os, urlparse, time

app = Flask(__name__)
app.secret_key = 'some_random_secret'
parse = Parse()

INSTAGRAM_CLIENT_ID = 'd18a0312ac06430cba43f02ccbf9c5d4'
INSTAGRAM_CLIENT_SECRET = '7a2040afd3044962a636ac001be5f5a2'

REDIRECT_URI_DEV = 'http://127.0.0.1:5000/igram_oauth_callback'
REDIRECT_URI_PROD = 'http://desolate-woodland-8107.herokuapp.com/igram_oauth_callback'
GRANT_TYPE = 'authorization_code'


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
    photo1 = None
    photo2 = None
    result = None

    if 'photo1' in request.form and 'photo2' in request.form and 'result' in request.form:
        photo1 = request.form['photo1']
        photo2 = request.form['photo2']
        result = request.form['result']

        # validate POST data for security
        if len(photo1) == 0 or len(photo2) == 0:
            return json.dumps({"errorMsg": "Invalid data"}), 400
        if result != 'win' and result != 'loss':
            return json.dumps({"errorMsg": "Invalid data"}), 400
    else:
        return json.dumps({"errorMsg": "Invalid data"}), 400

    print photo1, photo2, result

    # verify that media exists
    try:
        photo1 = Media.Query.get(objectId=photo1)
        photo2 = Media.Query.get(objectId=photo2)
    except QueryResourceDoesNotExist:
        return json.dumps({"errorMsg": "Invalid data"}), 400

    rating1 = None
    rating2 = None

    # if rating exists already, update it
    try:
        rating1 = Rating.Query.get(mediaId=photo1.objectId)
        rating2 = Rating.Query.get(mediaId=photo2.objectId)
    except QueryResourceDoesNotExist:
        rating1 = Rating(rating=BASE_RATING, mediaId=photo1.objectId)
        rating2 = Rating(rating=BASE_RATING, mediaId=photo2.objectId)

    ratings = update_rating(rating1, rating2, result)
    rating1.rating = ratings[0]
    rating2.rating = ratings[1]

    ratings = [rating1, rating2]
    try:
        batcher = ParseBatcher()
        batcher.batch_save(ratings)
    except:
        return json.dumps({"errorMsg": "Failed to save votes"}), 400

    return json.dumps({"success": True}), 200


def update_rating(rating1, rating2, result):
    pl_one = rating1.rating
    pl_two = rating2.rating

    eA = 1 / (1 + 10**((pl_two - pl_one)/400))
    eB = 1 / (1 + 10**((pl_one - pl_two)/400))

    print "expected: ", eA, eB

    if result == 'win':
        pl_one = pl_one + KC*(WIN - eA)
        pl_two = pl_two + KC*(LOSS - eB)
        print "pl_one: %d, pl_two: %d" % (pl_one, pl_two)
    if result == 'loss':
        pl_one = pl_one + KC*(LOSS - eA)
        pl_two = pl_two + KC*(WIN - eB)
        print "pl_one: %d, pl_two: %d" % (pl_one, pl_two)

    return [pl_one, pl_two]


@app.route("/new_round")
def new_round():
    new_players = get_new_players()
    players = []

    for player in new_players:
      images = ast.literal_eval(player.images)
      players.append({'objectId': player.objectId, 'images': images})

    print "players: ", players[0]['objectId'], players[1]['objectId']
    return json.dumps(players)


""" Returns a list containing two new players """
def get_new_players():
    all = Media.Query.all()
    count = 100 # all.count()
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
    return render_template('ratingtest.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
    parse = Parse()
