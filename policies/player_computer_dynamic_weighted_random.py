import random

from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from trick import Trick


# dynamic weighted random policy
# bids using a-priori winning probabilities of cards in hand (same as static policy)
# plays cards assessing the current trick and the current hand and calculates winning probabilities based on these
class PlayerComputerDynamicWeightedRandom(PlayerComputerWeightedRandom):

    def select_card(self, trick, bids, legal_cards, current_hand, played_cards, players):
        selected_card = None
        interval = 0
        probs_dict = {}
        for card in legal_cards:
            prob = card.calc_dynamic_win_prob(trick, played_cards, legal_cards, current_hand, players)
            probs_dict[card] = (interval, interval + prob)
            interval = interval + prob
        prob_sum = 0
        for v in probs_dict.values():
            prob_sum = prob_sum + v[1]
        # if there is zero chance of winning, calc "static loosing probs" and select card with highest loosing prob
        if prob_sum == 0:
            probs_dict = self.build_static_probs_interval_dict(cards=legal_cards, trump_suit=trick.trump_suit, players=players, win_prob=False)

        selected_card = self.select_card_in_static_probs_interval_dict(probs_dict)
        if selected_card is None:
            raise Exception('No card selected. A card must be selected. Exiting.')
        return selected_card
