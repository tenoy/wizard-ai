from policies.player_computer_weighted_random import PlayerComputerWeightedRandom


class PlayerComputerHeuristic(PlayerComputerWeightedRandom):

    def calculate_bid(self, round_nr=None, previous_bids=None, players=None, trump_suit=None):
        print('stub')

    def select_card(self, trick=None, bids=None, legal_cards=None, current_hand=None, played_cards=None, players=None):
        print('stub')

    def select_suit(self):
        print('stub')