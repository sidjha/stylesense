from app import parse
from apputils import last_monday
from parse import Media, Parse, Rating

MAX_DISPLAY = 5

def get_leaderboard():
  top_media = get_top_media()

  leaders = []

  for media in top_media:
    leader = {}
    leader['img_url'] = media.lowResolutionUrl
    leader['link'] = media.link
    leader['username'] = media.username
    leader['net_votes'] = media.netVotes
    leaders.append(leader)

  return leaders

def get_top_media():
  return Media.Query.all().order_by('-netVotes').limit(MAX_DISPLAY).filter(createdAt__gte=last_monday())
