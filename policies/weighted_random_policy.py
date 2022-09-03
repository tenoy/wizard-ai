import random
from enum_suit import Suit


class WeightedRandomPolicy():

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

        # bid = random.randint(0, round_nr)
        return bid

    @staticmethod
    def play(trick, leading_suit, trump_suit, bids, current_hand, contains_current_hand_leading_suit):
        legal_cards = []
        if leading_suit is None or leading_suit == Suit.JOKER or not contains_current_hand_leading_suit:
            # card_idx = random.randint(0, len(current_hand)-1)
            legal_cards.extend(current_hand)
        else:
            for card in current_hand:
                if card.suit == leading_suit or card.suit == Suit.JOKER:
                    legal_cards.append(card)
            # card_idx = random.randint(0, len(leading_suit_cards)-1)
        interval = 0
        probs_dict = {}
        for card in legal_cards:
            if card.suit == trump_suit:
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

        #selected_card = current_hand[card_idx]
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
