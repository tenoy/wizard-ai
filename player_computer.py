import random
from enum_suit import Suit
from player import Player


class PlayerComputer(Player):

 #   def __init__(self, number, player_type):
 #       super(PlayerComputer, self).__init__(number, player_type)

    def make_bid(self, round_nr, previous_bids, players, trump_suit):
        # sum of bids is not allowed to be equal to the number of the round
        bid = random.randint(0, round_nr)
        if self.is_valid_bid(bid, round_nr, previous_bids, players):
            return bid
        else:
            return self.make_bid(round_nr, previous_bids, players, trump_suit)

    def play(self, trick, leading_suit, trump_suit):
        if leading_suit is None or leading_suit == Suit.JOKER or not self.contains_current_hand_leading_suit(leading_suit):
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

    def select_suit(self):
        selected_suit = None
        while not self.is_valid_suit(selected_suit):
            rnd_idx = random.randint(0, len(self.current_hand) - 1)
            selected_suit = self.current_hand[rnd_idx].suit
        return selected_suit
