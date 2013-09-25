from flask import Flask, request, render_template, json, url_for, redirect, session
import urllib, urllib2
app = Flask(__name__)

CLIENT_ID = '77bdd37f87264ebea8c9a3178c9abd20'
CLIENT_SECRET = 'c0b4cfe4fb6949848bb8c022c164a369'
REDIRECT_URI_DEV = 'http://127.0.0.1:5000/igram_oauth_callback'
REDIRECT_URI_PROD = 'http://something.herokuapp.com/igram_oauth_callback'
GRANT_TYPE = 'authorization_code'

app.secret_key = 'some_random_secret'

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
        values = {'client_id': CLIENT_ID, 
                  'client_secret': CLIENT_SECRET,
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

if __name__ == '__main__':
    app.debug = True
    app.run()
