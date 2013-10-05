from parse import Media, Parse, Rating
from app import parse
from apputils import LinkedRand, parse_save_batch_objects, fetch_or_initialize_class
from rating import hot

BATCH_REQUEST_LIMIT = 50

def chunks(l, n):
  """ Yield successive n-sized chunks from l. """
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

def process_parse_saving_in_chunks(l):
  """
  Since Parse's API has a max limit on the size of each batch request,
  we must divide them into chunks of 50
  """
  dataset_size = len(l)
  chunk_count = 0
  l_chunks = chunks(l, BATCH_REQUEST_LIMIT)

  for chunk in l_chunks:
    print "Processing chunk %d of %d" % (chunk_count, dataset_size / BATCH_REQUEST_LIMIT)
    parse_save_batch_objects(chunk)
    chunk_count += 1


def run_bot():
  photos = []

  count = Media.Query.all().count()
  dataset_size = int(count*0.05)

  randint = LinkedRand(count)
  rand = randint()
  dataset = Media.Query.all().skip(rand).limit(dataset_size)

  print "Dataset size: %d, trying to fetch %d random photos" % (count, dataset_size)

  for photo in dataset:
    randint = LinkedRand(2)
    rand = randint()
    if rand == 0:
      photo.wins = photo.wins + 1
    else:
      photo.losses = photo.losses + 1
    photos.append(photo)


  print "Processing photos chunks..."
  process_parse_saving_in_chunks(photos)

  ratings = []
  for photo in photos:
    rating = fetch_or_initialize_class(Rating, photo.objectId)
    rating.rating = hot(photo.wins, photo.losses, photo.createdAt)
    ratings.append(rating)

  print "Processing ratings chunks..."
  process_parse_saving_in_chunks(ratings)


if __name__ == "__main__":
  run_bot()
