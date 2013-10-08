from datetime import datetime, timedelta
from math import log

epoch = datetime(1970, 1, 1)

HOT_THRESHOLDS = {
  'TOP': 0.8,
  'GOOD': 0.7,
  'AVERAGE': 0.6,
  'PASS': 0.5
}

def _epoch_seconds(date):
  """Returns the number of seconds from the epoch to date."""
  td = date - epoch
  return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

def _score(wins, losses):
  return wins - losses

def hot(wins, losses, date):
  """The hot formula"""
  website_launch_time = 1380585600
  s = _score(wins, losses)
  order = log(max(abs(s), 1), 10)
  sign = 1 if s > 0 else -1 if s < 0 else 0
  seconds = _epoch_seconds(date) - website_launch_time

  return round(order + sign * seconds / 45000, 7)
