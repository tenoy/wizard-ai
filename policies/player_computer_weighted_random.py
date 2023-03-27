import random
from enum_suit import Suit
from player_computer import PlayerComputer


# static weighted random policy
# bids using a-priori winning probabilities of cards in hand
# plays cards in a similar way
class PlayerComputerWeightedRandom(PlayerComputer):

    def calculate_bid(self, state):
        bid = 0
        for card in self.current_hand:
            rnd = random.uniform(0, 1)
            prob = card.calc_static_win_prob(self.current_hand, state.trick.trump_card, state.players_play_order, self)
            if rnd <= prob:
                bid = bid + 1

        return bid

    def recalculate_bid(self, state, bid):
        if bid == 0:
            bid = 1
        else:
            bid = bid + random.randint(-1, 1)
        return bid

    def select_card(self, state, legal_cards, played_cards=None):
        selected_card = None
        probs_dict = self.build_static_probs_interval_dict(cards=legal_cards, trump_card=state.trick.trump_card, players=state.players_play_order)
        prob_sum = 0
        for v in probs_dict.values():
            prob_sum = prob_sum + v[1]
        if prob_sum == 0:
            probs_dict = self.build_static_probs_interval_dict(cards=legal_cards, trump_card=state.trick.trump_card, players=state.players_play_order, win_prob=False)
        selected_card = self.select_card_in_static_probs_interval_dict(probs_dict)
        if selected_card is None:
            raise Exception('No card selected. A card must be selected. Exiting.')
        return selected_card

    def build_static_probs_interval_dict(self, cards, trump_card, players, win_prob=True):
        # build 'probability intervals' whose size correspond to their 'probability'
        interval = 0
        probs_dict = {}
        for card in cards:
            prob = card.calc_static_win_prob(self.current_hand, trump_card, players, self)
            if not win_prob:
                prob = 1 - prob
            probs_dict[card] = (interval, interval + prob)
            interval = interval + prob
        return probs_dict

    def select_card_in_static_probs_interval_dict(self, probs_dict):
        # get upper bound of all intervals
        # dicts are ordered / keep insertion order since python 3.7!
        interval = [*probs_dict.values()][-1][-1]
        rnd = random.uniform(0, interval)
        # get the corresponding card into which rnd falls from probs_dict
        selected_card = None
        for k, v in probs_dict.items():
            if v[0] <= rnd < v[1]:
                selected_card = k
                break
        return selected_card

    def select_suit(self, state):
        cards_without_joker = []
        for card in self.current_hand:
            if card.suit is not Suit.JOKER:
                cards_without_joker.append(card)

        if len(cards_without_joker) == 0:
            rnd_idx = random.randint(1, len(Suit) - 1)
            selected_suit = Suit(rnd_idx)
        else:
            rnd_idx = random.randint(0, len(cards_without_joker) - 1)
            selected_suit = cards_without_joker[rnd_idx].suit

        return selected_suit
