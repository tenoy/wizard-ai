import random
from enum_suit import Suit


class Random():

    @staticmethod
    def make_bid(round_nr):
        bid = random.randint(0, round_nr)
        return bid

    @staticmethod
    def play(trick, leading_suit, trump_suit, bids, current_hand, contains_current_hand_leading_suit):
        if leading_suit is None or leading_suit == Suit.JOKER or not contains_current_hand_leading_suit:
            # replace this with methods that select card given the current hand
            card_idx = random.randint(0, len(current_hand)-1)
        else:
            leading_suit_cards = []
            for card in current_hand:
                if card.suit == leading_suit or card.suit == Suit.JOKER:
                    leading_suit_cards.append(card)
            card_idx = random.randint(0, len(leading_suit_cards)-1)

        selected_card = current_hand[card_idx]
        return selected_card
