from parse import Media, Parse, Rating
from app import parse

def get_leaderboard(count):
	top_media = get_top_media(count)
	leaders = []
	for media in top_media:
		leader = {}
		leader['img_url'] = media.lowResolutionUrl
		leader['link'] = media.link
		leader['username'] = media.username
		leader['wins'] = media.wins
		leader['losses'] = media.losses
		leaders.append(leader)
	return leaders

def get_top_ratings(count):
	actual_count = Rating.Query.all().count()
	if count > actual_count:
		count = actual_count
	ratings = Rating.Query.all().order_by('-rating').limit(count)
	return ratings


def get_top_media(count):
	ratings = get_top_ratings(count)
	top_media = []
	for rating in ratings:
		media = Media.Query.get(objectId=rating.mediaId)
		top_media.append(media)
	return top_media
