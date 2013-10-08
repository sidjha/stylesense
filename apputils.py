from parse import Media, Parse, Rating, get_new_player
from parse_rest.connection import ParseBatcher
from parse_rest.query import QueryResourceDoesNotExist

import random

def parse_save_batch_objects(objects):
  try:
    batcher = ParseBatcher()
    batcher.batch_save(objects)
  except Exception as e:
    raise Exception(e)

def fetch_or_initialize_class(klass, photo_id):
  obj = None

  try:
    obj = klass.Query.get(mediaId=photo_id)
  except QueryResourceDoesNotExist:
    obj = klass(mediaId=photo_id)

  return obj

def verify_form_field(field_id, request):
  if field_id in request.form:
    field = request.form[field_id]

    if len(field) == 0:
      raise ValueError("Invalid data");

    return field
  else:
      raise ValueError("Invalid data");


class LinkedRand(object):
  def __init__(self, count, start=0):
    self.last = None
    self.count = count
    self.start = start

  def __call__(self):
    r = random.randint(self.start, self.count - 1)
    while r == self.last:
      r = random.randint(self.start, self.count - 1)
    self.last = r
    return r
