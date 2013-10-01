from __future__ import division
from flask import Flask, request, render_template, json, url_for, redirect, session
from parse import Media, Parse, Rating, get_new_player
from parse_rest.connection import ParseBatcher
from parse_rest.query import QueryResourceDoesNotExist
from rating import BASE_RATING, KC, WIN, LOSS, update_rating
from apputils import LinkedRand

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
    winner = None

    if 'photo1' in request.form and 'photo2' in request.form and 'winner' in request.form:
        photo1 = request.form['photo1']
        photo2 = request.form['photo2']
        winner = request.form['winner']

        # validate POST data for security
        if len(photo1) == 0 or len(photo2) == 0 or len(winner) == 0:
            return json.dumps({"errorMsg": "Invalid data"}), 400
    else:
        return json.dumps({"errorMsg": "Invalid data"}), 400

    print photo1, photo2, winner

    result = None
    if winner == photo1:
        result = 'win'
    if winner == photo2:
        result = 'loss'

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
    except QueryResourceDoesNotExist:
        rating1 = Rating(rating=BASE_RATING, mediaId=photo1.objectId)

    try:
        rating2 = Rating.Query.get(mediaId=photo2.objectId)
    except QueryResourceDoesNotExist:
        rating2 = Rating(rating=BASE_RATING, mediaId=photo2.objectId)

    ratings = update_rating(rating1, rating2, result)
    rating1.rating = ratings[0]
    rating2.rating = ratings[1]

    if result == 'win':
        photo1.wins = photo1.wins + 1
        photo2.losses = photo2.losses + 1
        
    if result == 'loss':
        photo2.wins = photo2.wins + 1
        photo1.losses = photo1.losses + 1

    # save all objects at once
    objects = [rating1, rating2, photo1, photo2]
    
    try:
        batcher = ParseBatcher()
        batcher.batch_save(objects)
    except Exception as e:
        print e
        return json.dumps({"errorMsg": "Votes could not be saved."}), 400

    return json.dumps({"success": True}), 200


@app.route("/new_round")
def new_round():
    new_players = get_new_players()
    players = []

    for player in new_players:
      #images = ast.literal_eval(player['images'])
      image = player['lowResolutionUrl']
      username = player['username']
      link = player['link']
      wins = player['wins']
      losses = player['losses']
      players.append({'objectId': player['objectId'], 
                      'image': image, 
                      'username': username, 
                      'link': link, 
                      'wins': wins,
                      'losses': losses})

    print "players: ", players[0]['objectId'], players[1]['objectId']
    return json.dumps(players)



def get_new_players():
    """ Returns a list containing two new players """
    most_recent = Media.Query.all().order_by('-createdAt').limit(1)

    if not most_recent.exists():
        return

    index = 0

    for obj in most_recent:
        index = obj.index + 1

    count = index
    randint = LinkedRand(count)
    rand1 = randint()
    rand2 = randint()

    try:
        player1 = get_new_player(rand1)
        player2 = get_new_player(rand2)
    except QueryResourceDoesNotExist:
        return json.dumps({"errorMsg": "Randomization failed"}), 400

    return [player1, player2]


@app.route("/test/rating")
def rating():
    return render_template('ratingtest.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
    parse = Parse()
