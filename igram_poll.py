from app import INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET
from instagram.client import InstagramAPI
from parse import Media, Parse
from parse_rest.connection import ParseBatcher

import time, sys

FOLLOWER_THRESHOLD = 200
HASHTAGS_THRESHOLD = 15

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
                             'netVotes': 0,
                             'standardResolutionUrl': obj.get_standard_resolution_url(),
                             'tags': obj.tags,
                             'username': obj.user.username,
                             'userId': obj.user.id,
                             'wins': 0})

    if media.followers < FOLLOWER_THRESHOLD:
      continue

    if len(media.tags) > HASHTAGS_THRESHOLD:
      continue

    if 'ootd' not in media.caption.lower():
      continue

    try:
      if not media.exists():
        media_list.append(media)
        print "Media %s queued for save" % n
        index += 1
        n += 1
    except Exception as e:
      print e
      print "ERROR: item could not be saved"
      continue

  if len(media_list) > 0:
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
  print "\nWaiting..."


if __name__ == "__main__":
  api = InstagramAPI(INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET)
  parse = Parse()

  loop_count = 1

  # get number of times to run poll() from args
  if len(sys.argv) == 2:
    loop_count = int(sys.argv[1])

  for i in xrange(loop_count):
    print "[%d/%d] Polling IG" % ((i + 1), loop_count)
    poll()

    time.sleep(5)  # sleep for a few seconds for server to get some new data...
