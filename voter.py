from parse import Media, Parse, Rating
from app import parse
from apputils import LinkedRand, parse_save_batch_objects, fetch_or_initialize_class
from rating import hot

def run_bot():
	photos = []

	count = Media.Query.all().count()
	dataset_size = int(count*0.05)

	randint = LinkedRand(count)
	rand = randint()
	dataset = Media.Query.all().skip(rand).limit(dataset_size)

	for photo in dataset:
		randint = LinkedRand(2)
		rand = randint()
		if rand == 0:
			photo.wins = photo.wins + 1
		else:
			photo.losses = photo.losses + 1
		photos.append(photo)
	print photos

	parse_save_batch_objects(photos)

	ratings = []
	for photo in photos:
		rating = fetch_or_initialize_class(Rating, photo.objectId)
		rating.rating = hot(photo.wins, photo.losses, photo.createdAt)
		ratings.append(rating)

	print ratings

	parse_save_batch_objects(ratings)