import random
from enum_suit import Suit


class RandomPolicy():

    @staticmethod
    def make_bid(round_nr):
        bid = random.randint(0, round_nr)
        return bid

    @staticmethod
    def play(legal_cards):
        card_idx = random.randint(0, len(legal_cards)-1)
        selected_card = legal_cards[card_idx]
        return selected_card

    @staticmethod
    def select_suit():
        rnd_idx = random.randint(1, len(Suit)-1)
        selected_suit = Suit(rnd_idx)
        return selected_suit
