from parse import Media, Parse, Rating
from app import parse
from apputils import LinkedRand, parse_save_batch_objects, fetch_or_initialize_class, last_monday
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

  this_week = Media.Query.filter(createdAt__gte=last_monday())
  this_week_count = this_week.count()

  most_recent = this_week.order_by('-createdAt').limit(1)
  latest_index = 0
  for obj in most_recent:
      latest_index = obj.index + 1
  print "index: ", latest_index
  dataset_size = int(this_week_count*0.1)
  randint = LinkedRand(latest_index, this_week_count - latest_index)
  rand = randint()
  print "rand: ", rand
  dataset = this_week.skip(rand).limit(dataset_size)

  print "Dataset size: %d, trying to fetch %d random photos" % (this_week_count, dataset_size)

  for photo in dataset:
    randint = LinkedRand(11)
    rand = randint()
    if any(rand == x for x in range(10)):
      photo.wins = photo.wins + 1
    else:
      if photo.losses != 0 and photo.wins / photo.losses < 0.5:
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
