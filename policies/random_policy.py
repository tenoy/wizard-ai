import random
from enum_suit import Suit


class RandomPolicy:

    @staticmethod
    def calculate_bid(round_nr):
        bid = random.randint(0, round_nr)
        return bid

    @staticmethod
    def recalculate_bid(round_nr):
        return RandomPolicy.calculate_bid(round_nr)

    @staticmethod
    def select_card(legal_cards):
        card_idx = random.randint(0, len(legal_cards)-1)
        selected_card = legal_cards[card_idx]
        return selected_card

    @staticmethod
    def select_suit():
        rnd_idx = random.randint(1, len(Suit)-1)
        selected_suit = Suit(rnd_idx)
        return selected_suit
