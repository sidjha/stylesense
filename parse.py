from parse_rest.connection import register
from parse_rest.datatypes import Object
from parse_rest.query import QueryResourceDoesNotExist

import json, httplib, urllib

PARSE_APPLICATION_ID = 'GGEI1UGiW8CqKXqovHbt4w9ajoJIVZl7N2uJwdDB'
PARSE_REST_API_KEY = 'ihituXdUkmnFDZaOu1M44FC4GFQ82ryKZkTx6KYO'

def get_new_player(index):
  connection = httplib.HTTPSConnection('api.parse.com', 443)
  params = urllib.urlencode({"keys": "lowResolutionUrl,username,link,netVotes",
            "where": json.dumps({
              "index": {
                "$gte": index, "$lte": index
              }
            }
          )})

  connection.connect()
  connection.request('GET', '/1/classes/Media?%s' % params, '', {
        "X-Parse-Application-Id": PARSE_APPLICATION_ID,
        "X-Parse-REST-API-Key": PARSE_REST_API_KEY,
      })

  result = json.loads(connection.getresponse().read())

  return result['results'][0]

# Used to connect to Parse
class Parse:
  def __init__(self):
    register(PARSE_APPLICATION_ID, PARSE_REST_API_KEY)


# Saves photos that have been repoted (i.e., they don't work)
class ReportedMedia(Object):
  pass


# Stores skipping information
class Skip(Object):
  pass


# Stores rating information
class Rating(Object):
  pass


# Stores image data retrieved from Instagram
class Media(Object):
  def update_parameters(self, details):
    for k, v in details.items():
      v = self._serialize_data(k, v)
      setattr(self, k, v)

  def exists(self):
    try:
      existing = Media.Query.get(instagramId=self.instagramId)
    except QueryResourceDoesNotExist:
      return False
    else:
      print "%s already exists" % self.instagramId
      return True

  def _serialize_data(self, k, v):
    if k == 'caption':
      if hasattr(v, 'text'):
        v = v.text
      else:
        v = ''
    elif type(v) is list:
      serialized = map(self._serialize_list, v)
      v = serialized
    elif type(v) is dict:
      serialized = self._serialize_dict(v)
      v = str(serialized)

    return v

  def _serialize_dict(self, obj):
    serialized = {}

    for k, v in obj.items():
      if hasattr(v, 'url'):
        serialized[k] =  {'height': v.height,
                          'url': v.url,
                          'width': v.width }
      else:
        serialized[k] = repr(v)

    return serialized

  def _serialize_list(self, obj):
    if hasattr(obj, 'name'):
      return obj.name
    else:
      return repr(obj)
