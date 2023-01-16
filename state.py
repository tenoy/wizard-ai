import copy
from collections import deque
from trick import Trick


class State:

    def __init__(self, players, round_nr, trick, deck, bids):
        self.players = deque()
        for player in players:
            player_copy = copy.deepcopy(player)
            self.players.append(player_copy)

        self.round_nr = round_nr
        self.trick = Trick(trump_suit=trick.trump_suit, leading_suit=trick.leading_suit, cards=list(trick.cards), played_by=list(trick.played_by))
        self.deck = list(deck)
        self.bids = dict(bids)
