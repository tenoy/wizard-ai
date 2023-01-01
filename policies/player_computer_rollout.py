from simulation import Simulation
from card import Card
from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_myopic import PlayerComputerMyopic
from state import State


class PlayerComputerRollout(PlayerComputerMyopic):

    def calculate_bid(self, round_nr=None, previous_bids=None, players=None, trump_suit=None):
        deck = []
        for i in range(1, 5, 1):
            for j in range(2, 15, 1):
                c = Card(Suit(i), Rank(j))
                deck.append(c)
                # print(c)

        for i in range(1, 5, 1):
            c = Card(Suit.JOKER, Rank.JESTER, i)
            deck.append(c)
            # print(c)

        for i in range(1, 5, 1):
            c = Card(Suit.JOKER, Rank.WIZARD, i)
            deck.append(c)

        state = State(players, round_nr, [], deck, {})
        Simulation.simulate_episode(state, 1, True)
        print('stub')