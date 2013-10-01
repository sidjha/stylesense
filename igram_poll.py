from app import INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET
from instagram.client import InstagramAPI
from parse import Media, Parse
from parse_rest.connection import ParseBatcher

import time

POLL_DELAY = 60 # in seconds
FOLLOWER_THRESHOLD = 200

api = None
parse = None

def preprocess_obj(obj):
  # add followers to object
  user = api.user(obj.user.id)
  followers = user.counts['followed_by']
  obj.followers = followers

  # verify 'tags' exist
  if not hasattr(obj, 'tags'):
    obj.tags = []

  return obj

def poll():
  recent_tags = api.tag_recent_media(tag_name="ootd")
  recent_media = recent_tags[0]
  count = len(recent_media)
  n = 0

  print "Processing %d recent media items" % count

  if count == 0:
    return

  index = 0
  most_recent = Media.Query.all().order_by('-createdAt').limit(1)

  for obj in most_recent:
    index = obj.index + 1

  media_list = []
  for obj in recent_media:
    obj = preprocess_obj(obj)

    media = Media()
    media.update_parameters({'caption': obj.caption,
                             'commentCount': obj.comment_count,
                             'comments': obj.comments,
                             'filterName': obj.filter,
                             'followers': obj.followers,
                             'images': obj.images,
                             'index': index,
                             'instagramId': obj.id,
                             'likeCount': obj.like_count,
                             'likes': obj.likes,
                             'link': obj.link,
                             'losses': 0,
                             'lowResolutionUrl': obj.images['low_resolution'].url,
                             'mediaCreatedTime': obj.created_time,
                             'standardResolutionUrl': obj.get_standard_resolution_url(),
                             'tags': obj.tags,
                             'username': obj.user.username,
                             'userId': obj.user.id,
                             'wins': 0})

    if media.followers < FOLLOWER_THRESHOLD:
      continue
    elif 'ootd' not in media.tags:
      continue

    if not media.exists():
      media_list.append(media)
      print "Media %s queued for save" % n
      index += 1
      n += 1

  try:
    batcher = ParseBatcher()
    batcher.batch_save(media_list)
  except Exception as e:
    print e
    print "ERROR: %d items could not be saved" % n
  else:
    print "%d items saved: " % n
    for media in media_list:
      print " Media (id: %s)" % media.objectId
  finally:
    print "Waiting.."


if __name__ == "__main__":
  print "Starting Instagram poller. Poll delay: %d" % POLL_DELAY

  api = InstagramAPI(INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET)
  parse = Parse()

  while True:
    poll()
    print '-' * 20
    time.sleep(POLL_DELAY)
