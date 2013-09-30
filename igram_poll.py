from app import INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET
from instagram.client import InstagramAPI
from parse import Media, Parse

import time

POLL_DELAY = 5 # in seconds
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
                             'mediaCreatedTime': obj.created_time,
                             'standardResolutionUrl': obj.get_standard_resolution_url(),
                             'lowResolutionUrl': obj.images['low_resolution'].url,
                             'tags': obj.tags,
                             'username': obj.user.username,
                             'userId': obj.user.id })

    if media.followers < FOLLOWER_THRESHOLD:
      continue
    elif 'ootd' not in media.tags:
      continue

    media.save()

    index += 1
    n += 1

    if media.objectId:
      print "Media saved successfully (id: %s)" % media.objectId

  print "%d items saved" % n


if __name__ == "__main__":
  print "Starting Instagram poller. Poll delay: %d" % POLL_DELAY

  api = InstagramAPI(INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET)
  parse = Parse()

  while True:
    poll()
    print '-' * 20
    time.sleep(POLL_DELAY)
