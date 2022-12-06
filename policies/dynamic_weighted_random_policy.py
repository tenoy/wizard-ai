import random
from enum_suit import Suit
from policies.weighted_random_policy import WeightedRandomPolicy
from utils import get_highest_legal_card, get_highest_card_in_trick


# dynamic weighted random policy
# bids using a-priori winning probabilities of cards in hand (same as static policy)
# plays cards assessing the current trick and the current hand and calculates winning probabilities based on these
class DynamicWeightedRandomPolicy(WeightedRandomPolicy):

    @staticmethod
    def make_bid(round_nr, current_hand, trump_suit):
        bid = WeightedRandomPolicy.make_bid(round_nr, current_hand, trump_suit)
        return bid

    @staticmethod
    def play(trick, leading_suit, trump_suit, bids, legal_cards, current_hand):
        # selection logic is the same as weighted random policy if trick is empty
        selected_card = None
        if len(trick) == 0:
            selected_card = WeightedRandomPolicy.play(trick, leading_suit, trump_suit, bids, legal_cards, current_hand)
        else:
            highest_card_legal = get_highest_legal_card(legal_cards, trump_suit, leading_suit)
            trick_extended = list(trick)
            trick_extended.append(highest_card_legal)
            highest_card_trick = get_highest_card_in_trick(trick_extended, trump_suit, leading_suit)
            # case where the highest legal card would be highest card in trick (so far)
            # note that the is operator is used here, since == would be wrong (e.g. both trick and hand contain wizard)
            if highest_card_trick is highest_card_legal:
                print('blub')
            else:
                print('bla')

            result = DynamicWeightedRandomPolicy.build_intervals(legal_cards, trump_suit, 1)
            probs_dict = result[0]
            interval = result[1]
            rnd = random.uniform(0, interval)
            # get the corresponding card into which rnd falls from probs_dict
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

    @staticmethod
    def build_intervals(legal_cards, trump_suit, win_prob_flag):
        # build 'probability intervals' whose size correspond to their probability
        interval = 0
        probs_dict = {}
        for card in legal_cards:
            if card.suit == trump_suit:
                if win_prob_flag == 1:
                    prob = card.win_prob_trump
                else:
                    prob = 1 - card.win_prob_trump
            else:
                if win_prob_flag == 1:
                    prob = card.win_prob
                else:
                    prob = 1 - card.win_prob
            probs_dict[card] = (interval, interval + prob)
            interval = interval + prob
        return probs_dict, interval
