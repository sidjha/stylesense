from parse import Media, Parse, Rating, get_new_player
from parse_rest.connection import ParseBatcher
from parse_rest.query import QueryResourceDoesNotExist
from parse_rest.datatypes import Date
from datetime import datetime, timedelta

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

def last_monday():
  """ Returns last Monday in UTC ISO 8601 formatted JSON object """
  today = datetime.utcnow()

  # get monday at midnight
  mon = today - timedelta(days=today.weekday())
  mon = mon.replace(hour=0, minute=0, second=0, microsecond=0)

  date_mon = Date(mon)
  ts = date_mon._to_native()

  return ts

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
