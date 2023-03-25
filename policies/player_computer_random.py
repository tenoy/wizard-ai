import random
from enum_suit import Suit
from player_computer import PlayerComputer


class PlayerComputerRandom(PlayerComputer):

    def calculate_bid(self, state):
        bid = random.randint(0, state.round_nr)
        return bid

    def recalculate_bid(self, state, bid):
        return self.calculate_bid(state)

    def select_card(self, state, legal_cards, played_cards=None):
        card_idx = random.randint(0, len(legal_cards)-1)
        selected_card = legal_cards[card_idx]
        return selected_card

    def select_suit(self, state):
        rnd_idx = random.randint(1, len(Suit)-1)
        selected_suit = Suit(rnd_idx)
        return selected_suit
