from __future__ import division
from flask import Flask, request, render_template, json, url_for, redirect, session
from flask.ext.assets import Environment, Bundle
from parse import Media, Parse, Rating, Skip, ReportedMedia, get_new_player
from parse_rest.connection import ParseBatcher
from parse_rest.query import QueryResourceDoesNotExist
from rating import hot
from apputils import LinkedRand, verify_form_field, fetch_or_initialize_class, parse_save_batch_objects, last_monday

import ast, urllib, urllib2, os, urlparse, time

app = Flask(__name__)
app.secret_key = 'some_random_secret'
assets = Environment(app)
parse = Parse()

js = Bundle('js/stylesense.js', filters='jsmin', output='js/jsmin.js')
assets.register('js_all', js)

css = Bundle('css/styles.css', 'css/grids.css', filters='cssmin', output='css/cssmin.css')
assets.register('css_all', css)

import leaderboard

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


@app.route("/skip_round", methods=['POST'])
def skip_round():
  photo1 = 'photo1'
  photo2 = 'photo2'

  try:
    photo1 = verify_form_field(photo1, request)
    photo2 = verify_form_field(photo2, request)
  except ValueError:
    return json.dumps({"errorMsg": "Invalid form data"}), 400

  try:
    photo1 = Media.Query.get(objectId=photo1)
    photo2 = Media.Query.get(objectId=photo2)
  except QueryResourceDoesNotExist:
    return json.dumps({"errorMsg": "Invalid photo data"}), 400

  # update skip counters
  skip1 = fetch_or_initialize_class(Skip, photo1.objectId)
  skip2 = fetch_or_initialize_class(Skip, photo2.objectId)

  for skip in [skip1, skip2]:
    if not skip.objectId:
      skip.skips = 1
    else:
      skip.skips += 1

  try:
    parse_save_batch_objects([skip1, skip2])
  except Exception as e:
    print e
    return json.dumps({"errorMsg": "Votes could not be saved."}), 400

  return json.dumps({"success": True}), 200


@app.route("/report_bad_image", methods=['POST'])
def report_bad_image():
  bad_photo = 'objectId'

  try:
    bad_photo = verify_form_field(bad_photo, request)
  except ValueError:
    return json.dumps({"errorMsg": "Invalid form data"}), 400

  try:
    bad_photo = Media.Query.get(objectId=bad_photo)
  except QueryResourceDoesNotExist:
    return json.dumps({"errorMsg": "Invalid photo data"}), 400

  report = fetch_or_initialize_class(ReportedMedia, bad_photo.objectId)

  if report.objectId:
    report.reports += 1
  else:
    report.reports = 1
    report.mediaId = bad_photo.objectId

  report.save()

  return json.dumps({"success": True}), 200


@app.route("/tally_round", methods=['POST'])
def tally_round():
    photo1 = 'photo1'
    photo2 = 'photo2'
    winner = 'winner'

    try:
      photo1 = verify_form_field(photo1, request)
      photo2 = verify_form_field(photo2, request)
      winner = verify_form_field(winner, request)
    except ValueError:
      return json.dumps({"errorMsg": "Invalid form data"}), 400

    # print photo1, photo2, winner

    # verify that media exists
    try:
      photo1 = Media.Query.get(objectId=photo1)
      photo2 = Media.Query.get(objectId=photo2)
    except QueryResourceDoesNotExist:
      return json.dumps({"errorMsg": "Invalid photo data"}), 400

    rating1 = fetch_or_initialize_class(Rating, photo1.objectId)
    rating2 = fetch_or_initialize_class(Rating, photo2.objectId)

    result = None

    if winner == photo1.objectId:
      result = 'win'
      photo1.wins += 1
      photo2.losses += 1

    if winner == photo2.objectId:
      result = 'loss'
      photo2.wins += 1
      photo1.losses += 1

    photo1.netVotes = photo1.wins - photo1.losses
    photo2.netVotes = photo2.wins - photo2.losses

    # update score of winner and loser
    rating1.rating = hot(photo1.wins, photo1.losses, photo1.createdAt)
    rating2.rating = hot(photo2.wins, photo2.losses, photo2.createdAt)

    # save all objects at once
    try:
      parse_save_batch_objects([rating1, rating2, photo1, photo2])
    except Exception as e:
      print e
      return json.dumps({"errorMsg": "Votes could not be saved."}), 400

    return json.dumps({"success": True}), 200


@app.route("/new_round")
def new_round():
    new_players = get_new_players()
    players = []

    for player in new_players:
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

    #print "players: ", players[0]['objectId'], players[1]['objectId']
    return json.dumps(players)


@app.route("/leaderboard")
def get_leaderboard():
    leaders = leaderboard.get_leaderboard(5)
    return json.dumps(leaders)

def get_new_players():
    """ Returns a list containing two new players """
    # Get num of photos taken since timestamp
    timestamp = last_monday()
    this_weeks_count = Media.Query.filter(createdAt__gte=timestamp).count()

    # Determine the latest 'index'
    most_recent = Media.Query.all().order_by('-createdAt').limit(1)
    if not most_recent.exists():
        return
    index = 0
    for obj in most_recent:
        index = obj.index + 1

    # Pick randomly from only this week's photos
    count = index
    start = count - this_weeks_count
    randint = LinkedRand(count, count - this_weeks_count)
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
