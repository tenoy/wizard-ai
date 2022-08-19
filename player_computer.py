import random
from player import Player
from policies.random import Random


class PlayerComputer(Player):

    def __init__(self, number, player_type, policy):
        super(PlayerComputer, self).__init__(number, player_type)
        self.policy = policy

    def make_bid(self, round_nr, previous_bids, players, trump_suit):
        # sum of bids is not allowed to be equal to the number of the round
        # bid = random.randint(0, round_nr)
        match self.policy:
            case 'random':
                bid = Random.make_bid(round_nr)
                while not self.is_valid_bid(bid, round_nr, previous_bids, players):
                    bid = Random.make_bid(round_nr)
        return bid

    def play(self, trick, leading_suit, trump_suit, bids):
        hand_contains_leading_suit = self.contains_current_hand_leading_suit(leading_suit)
        match self.policy:
            case 'random':
                selected_card = Random.play(trick, leading_suit, trump_suit, bids, self.current_hand, hand_contains_leading_suit)

        self.played_card = selected_card
        self.current_hand.remove(selected_card)
        return selected_card

    def select_suit(self):
        selected_suit = None
        while not self.is_valid_suit(selected_suit):
            rnd_idx = random.randint(0, len(self.current_hand) - 1)
            selected_suit = self.current_hand[rnd_idx].suit
        return selected_suit
