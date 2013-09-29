# Elo Rating System constants
BASE_RATING = 1400
KC = 32
WIN = 1
LOSS = 0

def update_rating(rating1, rating2, result):
    pl_one = rating1.rating
    pl_two = rating2.rating

    eA = 1 / (1 + 10**((pl_two - pl_one)/400))
    eB = 1 / (1 + 10**((pl_one - pl_two)/400))

    print "expected: ", eA, eB

    if result == 'win':
        pl_one = pl_one + KC*(WIN - eA)
        pl_two = pl_two + KC*(LOSS - eB)
        print "pl_one: %d, pl_two: %d" % (pl_one, pl_two)
    if result == 'loss':
        pl_one = pl_one + KC*(LOSS - eA)
        pl_two = pl_two + KC*(WIN - eB)
        print "pl_one: %d, pl_two: %d" % (pl_one, pl_two)

    return [pl_one, pl_two]
