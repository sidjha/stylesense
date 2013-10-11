from app import INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET
from instagram.client import InstagramAPI
from random import randint
from time import sleep

import json, sys

def auth():
  redirect_uri = "http://stylesen.se/"
  scope = ["relationships"]

  api = InstagramAPI(client_id=INSTAGRAM_CLIENT_ID, client_secret=INSTAGRAM_CLIENT_SECRET, redirect_uri=redirect_uri)
  redirect_uri = api.get_authorize_login_url(scope=scope)

  print "Visit this page and authorize access in your browser:\n", redirect_uri

  code = raw_input("Paste in code in query string after redirect: ").strip()

  access_token = api.exchange_code_for_access_token(code)

  return access_token

def api(access_token=None):
  if not access_token:
    access_token = auth()[0]
    print "Access token:\n", access_token

  api = InstagramAPI(access_token=access_token)

  return api

def follow(data, api):
  user_ids = set()

  for row in data['results']:
    user_ids.add(row['userId'])

  while user_ids:
    user_id = user_ids.pop()

    print "Following %s" % user_id

    try:
      api.follow_user(user_id=user_id)
    except Exception as e:
      print "Error saving..."
      print e
      user_ids.add(user_id)

    delay = randint(30, 90)
    print "Sleeping for %d seconds" % delay
    sleep(delay)


if __name__ == "__main__":
  json_data = open('Media.json')
  data = json.load(json_data)

  access_token = None

  if len(sys.argv) == 2:
    access_token = sys.argv[1]

  api = api(access_token)
  follow(data, api)

  json_data.close()
