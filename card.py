from enum_rank import Rank
from enum_suit import Suit


class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    #used only to compare cards of same suit
    def __gt__(self, other):
        return self.rank > other.rank

    def __str__(self):
        return str(self.rank) + ' ' + str(self.suit)






