import random
from enum_suit import Suit
from player_computer import PlayerComputer


class PlayerComputerRandom(PlayerComputer):

    def calculate_bid(self, round_nr, previous_bids, players, trump_suit):
        bid = random.randint(0, round_nr)
        return bid

    def recalculate_bid(self, bid, round_nr, previous_bids, players, trump_suit):
        return self.calculate_bid(round_nr, previous_bids, players, trump_suit)

    def select_card(self, trick, bids, legal_cards, current_hand, played_cards, number_of_players):
        card_idx = random.randint(0, len(legal_cards)-1)
        selected_card = legal_cards[card_idx]
        return selected_card

    def select_suit(self):
        rnd_idx = random.randint(1, len(Suit)-1)
        selected_suit = Suit(rnd_idx)
        return selected_suit
