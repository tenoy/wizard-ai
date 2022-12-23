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
            interval = 0
            for card in probs_dict.keys():
                if card.suit == trick.trump_suit:
                    prob = 1 - card.win_prob_trump
                else:
                    prob = 1 - card.win_prob
                probs_dict[card] = (interval, interval + prob)
                interval = interval + prob
        rnd = random.uniform(0, interval)
        # get the corresponding card into which rnd falls from probs_dict
        for k, v in probs_dict.items():
            if v[0] <= rnd < v[1]:
                selected_card = k
                break

        if selected_card is None:
            raise Exception('No card selected. A card must be selected. Exiting.')
        return selected_card
