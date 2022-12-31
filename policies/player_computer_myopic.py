import random

from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom


class PlayerComputerHeuristic(PlayerComputerWeightedRandom):

    def calculate_bid(self, round_nr=None, previous_bids=None, players=None, trump_suit=None):
        bid = 0
        for card in self.current_hand:
            if card.rank == Rank.WIZARD:
                bid = bid + 1
            else:
                prob = card.calc_static_win_prob(current_hand=self.current_hand, trump_suit=trump_suit, players=players)
                if prob >= 0.5:
                    bid = bid + 1
        return bid

    def select_card(self, trick=None, bids=None, legal_cards=None, current_hand=None, played_cards=None, players=None):
        if self.current_tricks_won < self.current_bid:
            probs_dict = {}
            for card in legal_cards:
                probs_dict[card] = card.calc_dynamic_win_prob(trick=trick, cards_played=played_cards, current_hand=self.current_hand, cards_legal=legal_cards, players=players)
            prob_sum = 0
            for v in probs_dict.values():
                prob_sum = prob_sum + v
            if prob_sum == 0:
                probs_dict = self.build_static_probs_dict(cards=legal_cards, trump_suit=trick.trump_suit, players=players, win_prob=False)
        else:
            probs_dict = self.build_static_probs_dict(cards=legal_cards, trump_suit=trick.trump_suit, players=players, win_prob=False)
        selected_card = max(probs_dict, key=probs_dict.get)
        return selected_card

    #trick, cards_played, cards_legal, current_hand, players
    def build_static_probs_dict(self, cards, trump_suit, players, win_prob=True):
        probs_dict = {}
        for card in cards:
            prob = card.calc_static_win_prob(self.current_hand, trump_suit, players)
            if not win_prob:
                prob = 1 - prob
            probs_dict[card] = prob
        return probs_dict

    def select_suit(self):
        suit_rank_sum_dict = {}
        for card in self.current_hand:
            if card.suit != Suit.JOKER:
                suit_rank_sum = suit_rank_sum_dict.setdefault(card.suit, 0)
                suit_rank_sum_dict[card.suit] = suit_rank_sum + card.rank
        if len(suit_rank_sum_dict) > 0:
            selected_suit = max(suit_rank_sum_dict, key=suit_rank_sum_dict.get)
        else:
            rnd_idx = random.randint(1, len(Suit) - 1)
            selected_suit = Suit(rnd_idx)
        return selected_suit
