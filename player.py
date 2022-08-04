import random

from enum_suit import Suit


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.current_hand = []
        self.current_bid = -1
        self.current_tricks_won = 0
        self.score = 0
        self.played_card = None

    def make_bid(self, round_nr, previous_bids, players):
        # sum of bids is not allowed to be equal to the number of the round
        bid = random.randint(0, round_nr)
        if len(previous_bids) == len(players) - 1:
            while sum(previous_bids) + bid == round_nr:
                bid = random.randint(0, round_nr)

        return bid

    def contains_current_hand_leading_suit(self, leading_suit):
        for card in self.current_hand:
            if card.suit == leading_suit:
                return True
        return False

    def play(self, trick, leading_suit):
        if leading_suit is None or not self.contains_current_hand_leading_suit(leading_suit):
            # replace this with methods that select card given the current hand
            card_idx = random.randint(0, len(self.current_hand)-1)
        else:
            leading_suit_cards = []
            for card in self.current_hand:
                if card.suit == leading_suit or card.suit == Suit.JOKER:
                    leading_suit_cards.append(card)
            card_idx = random.randint(0, len(leading_suit_cards)-1)

        selected_card = self.current_hand[card_idx]
        self.played_card = selected_card
        self.current_hand.remove(selected_card)
        return selected_card






