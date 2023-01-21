import copy
from collections import deque
from trick import Trick


class State:

    def __init__(self, players_deal_order, round_nr, trick, deck, bids):
        # deal order is the deep copy list (necessary for rollout policy)
        self.players_deal_order = deque()
        for player in players_deal_order:
            player_copy = copy.deepcopy(player)
            self.players_deal_order.append(player_copy)
        # bid and play order are shallow copies of deal order deep copy
        self.players_bid_order = deque(self.players_deal_order)
        self.players_play_order = deque(self.players_deal_order)
        self.round_nr = round_nr
        self.trick = Trick(trump_suit=trick.trump_suit, leading_suit=trick.leading_suit, cards=list(trick.cards), played_by=list(trick.played_by))
        self.deck = list(deck)
        self.bids = dict(bids)
