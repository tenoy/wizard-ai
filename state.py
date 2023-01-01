from collections import deque

from trick import Trick


class State:

    def __init__(self, players, round_nr, trick, deck, bids):
        self.players = deque(players)
        self.round_nr = round_nr
        self.max_number_of_rounds = int(60 / len(players))
        self.trick = Trick(trump_suit=trick.trump_suit, leading_suit=trick.leading_suit, cards=trick.cards, played_by=trick.played_by)
        self.deck = list(deck)
        self.bids = dict(bids)
