import random
from enum_suit import Suit


# static weighted random policy
# bids using a-priori winning probabilities of cards in hand
# plays cards in a similar way
class WeightedRandomPolicy:

    @staticmethod
    def make_bid(round_nr, current_hand, trump_suit):
        bid = 0
        for card in current_hand:
            rnd = random.uniform(0, 1)
            if card.suit == trump_suit or trump_suit is None:
                prob = card.win_prob_trump
            else:
                prob = card.win_prob
            if rnd <= prob:
                bid = bid + 1

        return bid

    @staticmethod
    def play(trick, bids, legal_cards):
        # build 'probability intervals' whose size correspond to their 'probability'
        interval = 0
        probs_dict = {}
        for card in legal_cards:
            if card.suit == trick.trump_suit:
                prob = card.win_prob_trump
            else:
                prob = card.win_prob
            probs_dict[card] = (interval, interval + prob)
            interval = interval + prob
        rnd = random.uniform(0, interval)
        # get the corresponding card into which rnd falls from probs_dict
        selected_card = None
        for k, v in probs_dict.items():
            if v[0] <= rnd < v[1]:
                selected_card = k
                break
        if selected_card is None:
            raise Exception('No card selected. A card must be selected. Exiting.')
        return selected_card

    @staticmethod
    def select_suit(current_hand):
        cards_without_joker = []
        for card in current_hand:
            if card.suit is not Suit.JOKER:
                cards_without_joker.append(card)

        if len(cards_without_joker) == 0:
            rnd_idx = random.randint(1, len(Suit) - 1)
            selected_suit = Suit(rnd_idx)
        else:
            rnd_idx = random.randint(0, len(cards_without_joker)-1)
            selected_suit = cards_without_joker[rnd_idx].suit

        return selected_suit
