import random
from collections import deque
from random import sample

from simulation import Simulation
from card import Card
from enum_rank import Rank
from enum_suit import Suit
from player_computer import PlayerComputer
from player_human import PlayerHuman
from policies.player_computer_dynamic_weighted_random import PlayerComputerDynamicWeightedRandom
from policies.player_computer_myopic import PlayerComputerMyopic
from policies.player_computer_random import PlayerComputerRandom
from policies.player_computer_rollout import PlayerComputerRollout
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from state import State
from trick import Trick
import datetime

deck = []
for i in range(1, 5, 1):
    for j in range(2, 15, 1):
        c = Card(Suit(i), Rank(j))
        deck.append(c)
        #print(c)

for i in range(1, 5, 1):
    c = Card(Suit.JOKER, Rank.JESTER, i)
    deck.append(c)
    #print(c)

for i in range(1, 5, 1):
    c = Card(Suit.JOKER, Rank.WIZARD, i)
    deck.append(c)
    #print(c)

# put in game class or something similar
number_of_players = 2
players_initial_order = deque()

players_initial_order.append(PlayerComputerRandom('computer', "random"))
players_initial_order.append(PlayerComputerWeightedRandom('computer', "weighted_random"))
players_initial_order.append(PlayerComputerDynamicWeightedRandom('computer', "dynamic_weighted_random"))
players_initial_order.append(PlayerComputerMyopic('computer', "heuristic"))
players_initial_order.append(PlayerComputerRollout('computer', "rollout"))
# players_initial_order.append(PlayerComputerDynamicWeightedRandom(4, 'computer', "dynamic_weighted_random"))
# players_initial_order.append(PlayerComputer(1, 'computer', 'random'))
# players_initial_order.append(PlayerComputer(2, 'computer', 'weighted_random'))
# players_initial_order.append(PlayerComputer(3, 'computer', 'dynamic_weighted_random'))
# players_initial_order.append(PlayerComputer(4, 'computer', 'dynamic_weighted_random'))
#players_initial_order.append(PlayerComputer(4, 'computer', 'dynamic_weighted_random'))
#players_initial_order.append(PlayerComputer(5, 'computer', 'dynamic_weighted_random'))
#players_initial_order.append(PlayerComputer(6, 'computer', 'dynamic_weighted_random'))
#players_initial_order.append(PlayerHuman(7, 'human'))

timestamp_start = datetime.datetime.now()

s0 = State(players_initial_order, 1, Trick(), deck, {})
winning_cards = {}
number_of_rounds = int(60 / len(players_initial_order))
for i in range(0, 1000):
    Simulation.simulate_episode(s0, number_of_rounds)
timestamp_end = datetime.datetime.now()
delta = timestamp_end - timestamp_start
print(f"Time difference is {delta.total_seconds()} seconds")
print('done')


