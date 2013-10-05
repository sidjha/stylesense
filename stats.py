from parse import Media, Skip, Rating
from app import parse
import datetime

QUERY_SIZE = 5

def most_skipped():
	mostskipped = Skip.Query.all().limit(QUERY_SIZE).order_by("-skips")
	skipped_media = []
	for item in mostskipped:
		media = Media.Query.get(objectId=item.mediaId)
		skipped_media.append({'media': media, 'skips': item.skips})

	print "Most skipped pictures (descending)"
	for i in range(0,20):
		print "-",
	print "\r"

	for item in skipped_media:
		media = item['media']
		skips = item['skips']
		print skips, " skips: ", media.link, " by ", media.username
	print "\r"

	return skipped_media

def most_wins():
	mostwins = Media.Query.all().limit(5).order_by('-wins')

	print "Pictures with most wins (descending)"
	for i in range(0,20):
		print "-",
	print "\r"

	for photo in mostwins:
		print photo.wins, " wins: ", photo.link, " by ", photo.username
	print "\r"
	
	return mostwins

def most_losses():
	mostlosses = Media.Query.all().limit(5).order_by('-losses')

	print "Pictures with most losses (descending)"
	for i in range(0,20):
		print "-",
	print "\r"

	for photo in mostlosses:
		print photo.losses, " losses: ", photo.link, " by ", photo.username
	print "\r"
	
	return mostlosses

def top_rated():
	toprated = Rating.Query.all().limit(5).order_by('-rating')

	print "Top rated pictures (descending)"
	for i in range(0,20):
		print "-",
	print "\r"

	photoIds = []
	for rating in toprated:
		photoId = {}
		photoId['id'] = rating.mediaId
		photoId['rating'] = rating.rating
		photoIds.append(photoId)

	for photoId in photoIds:
		photo = Media.Query.get(objectId=photoId['id'])
		print photoId['rating'], ": ", photo.link, " by ", photo.username

	return photoIds

if __name__ == '__main__':
	for i in range(0,20):
		print "-",
	print "\r"
	print "STYLESENSE STATS FOR %s" % datetime.date.today()
	for i in range(0,20):
		print "-",
	print "\r"

	top_rated()
	most_skipped()
	most_wins()
	most_losses()

	print "\r"
