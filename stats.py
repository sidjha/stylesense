from parse import Media, Skip
from app import parse
import datetime

def most_skipped():
	QUERY_SIZE = 5
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
	QUERY_SIZE = 5
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
	QUERY_SIZE = 5
	mostlosses = Media.Query.all().limit(5).order_by('-losses')

	print "Pictures with most losses (descending)"
	for i in range(0,20):
		print "-",
	print "\r"

	for photo in mostlosses:
		print photo.losses, " losses: ", photo.link, " by ", photo.username
	print "\r"
	
	return mostlosses

if __name__ == '__main__':
	for i in range(0,20):
		print "-",
	print "\r"
	print "STYLESENSE STATS FOR %s" % datetime.date.today()
	for i in range(0,20):
		print "-",
	print "\r"

	most_skipped()
	most_wins()
	most_losses()
	print "\r"
