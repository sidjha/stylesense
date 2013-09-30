import random

class LinkedRand(object):
    def __init__(self, count):
        self.last = None
        self.count = count

    def __call__(self):
        r = random.randint(0, self.count - 1)
        while r == self.last:
            r = random.randint(0, self.count - 1)
        self.last = r
        return r