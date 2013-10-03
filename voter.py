from parse import Media, Parse
from app import parse
from parse_rest.connection import ParseBatcher

def run_bot():
	photos = []

	count = Media.Query.all().count()
	dataset_size = int(count*0.05)
	dataset = Media.Query.all().limit(dataset_size)

	for photo in dataset:
		photo.wins = photo.wins + 1
		photos.append(photo)

	try:
		ParseBatcher.batch_save(photos)
	except e:
		print "ERROR: " + e