import numpy
import json

def hashtags_distribution(data):
  """Displays the distribution of hashtag count to number of photos"""

  tags_count = {}
  tags_to_objectid = {}
  hashtag_counts = []

  n = len(data['results'])
  avg = 0

  for row in data['results']:
    num_tags = len(row['tags'])

    if num_tags not in tags_to_objectid:
      tags_to_objectid[num_tags] = []
      tags_count[num_tags] = 0

    tags_to_objectid[num_tags].append(row['objectId'])
    tags_count[num_tags] += 1

    avg += num_tags
    hashtag_counts.append(num_tags)

  for k, v in tags_count.items():
    print "%d hashtags: %d rows" % (k, v)

  # compute average
  avg = avg / n

  sorted(hashtag_counts)

  print "Total rows: %d" % n
  print "Average # of hashtags: %d" % avg
  print "Median # of hashtags: %d" % numpy.median(hashtag_counts)

if __name__ == "__main__":
  # get a JSON dump of data to avoid doing thousands of Parse queries
  json_data = open('Media.json')
  data = json.load(json_data)

  hashtags_distribution(data)

  json_data.close()
