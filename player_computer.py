import random

from enum_suit import Suit
from player import Player
from policies.random_policy import RandomPolicy
from policies.weighted_random_policy import WeightedRandomPolicy


class PlayerComputer(Player):

    def __init__(self, number, player_type, policy):
        super(PlayerComputer, self).__init__(number, player_type)
        self.policy = policy

    def make_bid(self, round_nr, previous_bids, players, trump_suit):
        # sum of bids is not allowed to be equal to the number of the round
        # bid = random.randint(0, round_nr)
        match self.policy:
            case 'random':
                bid = RandomPolicy.make_bid(round_nr)
                while not self.is_valid_bid(bid, round_nr, previous_bids, players):
                    bid = RandomPolicy.make_bid(round_nr)
            case 'weighted_random':
                bid = WeightedRandomPolicy.make_bid(round_nr, self.current_hand, trump_suit)
                while not self.is_valid_bid(bid, round_nr, previous_bids, players):
                    bid = bid + random.randint(-1, 1)
        return bid

    def play(self, trick, leading_suit, trump_suit, bids):
        #prepare set of cards that are allowed to play so that the policies dont have to deal with that again and again
        legal_cards = []
        if leading_suit is None or leading_suit == Suit.JOKER or not self.contains_current_hand_leading_suit(leading_suit):
            legal_cards.extend(self.current_hand)
        else:
            for card in self.current_hand:
                if card.suit == leading_suit or card.suit == Suit.JOKER:
                    legal_cards.append(card)
        match self.policy:
            case 'random':
                selected_card = RandomPolicy.play(trick, leading_suit, trump_suit, bids, legal_cards, self.current_hand)
            case 'weighted_random':
                selected_card = WeightedRandomPolicy.play(trick, leading_suit, trump_suit, bids, legal_cards, self.current_hand)

        self.played_card = selected_card
        self.current_hand.remove(selected_card)
        return selected_card

    def select_suit(self):
        match self.policy:
            case 'random':
                selected_suit = RandomPolicy.select_suit()
            case 'weighted_random':
                selected_suit = WeightedRandomPolicy.select_suit(self.current_hand)
        return selected_suit
