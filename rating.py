# cli implementation of rating system
from __future__ import division
from random import randint
import sys

BASE_RATING = 1400
KC = 32
WIN = 1
LOSS = 0

def start():
	numPlayers = int(raw_input('how many players '))
	players = []

	for i in range(0, numPlayers):
		players.append(BASE_RATING)

	print 'original=', players

	command = raw_input('press n to play a new round. q to quit ')
	while command is not 'q':
		if command is 'n':
			pl_1_idx = randint(0, numPlayers-1)
			pl_2_idx = randint(0, numPlayers-1)
			pl_1 = players[pl_1_idx]
			pl_2 = players[pl_2_idx]

			winner = raw_input('choose winner: a or b ')
			while winner is not 'a' and (winner is not 'b'):
				winner = raw_input('please choose winner: a or b ')
			if winner is 'a':
				updateRating(players, pl_1_idx, pl_2_idx, WIN)
			if winner is 'b':
				updateRating(players, pl_1_idx, pl_2_idx, LOSS)
			print 'new score: ', players

			command = raw_input('press n to play a new round. q to quit ')
	sys.exit()

def updateRating(players, player1_idx, player2_idx, result):
	eA = 1 / (1 + 10**((players[player2_idx] - players[player1_idx])/400))
	eB = 1 / (1 + 10**((players[player1_idx] - players[player2_idx])/400))
	if result is WIN:
		players[player1_idx] = players[player1_idx] + KC*(WIN - eA)
		players[player2_idx] = players[player2_idx] + KC*(LOSS - eB)
	if result is LOSS:
		players[player1_idx] = players[player1_idx] + KC*(LOSS - eA)
		players[player2_idx] = players[player2_idx] + KC*(WIN - eB)


if __name__ == '__main__':
	start()