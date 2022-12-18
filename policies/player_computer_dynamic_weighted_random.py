import random

from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from policies.weighted_random_policy import WeightedRandomPolicy
from trick import Trick


# dynamic weighted random policy
# bids using a-priori winning probabilities of cards in hand (same as static policy)
# plays cards assessing the current trick and the current hand and calculates winning probabilities based on these
class PlayerComputerDynamicWeightedRandom(PlayerComputerWeightedRandom):

    def select_card(self, trick, bids, legal_cards, current_hand, played_cards, players):
        # selection logic is the same as weighted random policy if trick is empty
        selected_card = None
        #highest_card_legal = self.get_highest_legal_card(legal_cards, trick.trump_suit, trick.leading_suit)
        #trick_extended = Trick(trick.trump_suit, trick.leading_suit)
        #trick_extended.cards = list(trick.cards)
        #trick_extended.cards.append(highest_card_legal)
        #highest_card_trick = trick_extended.get_highest_trick_card()
        # check if the highest legal card would be the highest card in trick (so far)
        # note that the is operator is used here, since == would be wrong (e.g. both trick and hand contain wizard)
        #has_highest_card = highest_card_trick is highest_card_legal
        interval = 0
        probs_dict = {}
        for card in legal_cards:
            prob = card.calc_dynamic_win_prob(trick, played_cards, legal_cards, current_hand, players)
            probs_dict[card] = (interval, interval + prob)
            interval = interval + prob
        prob_sum = 0
        for v in probs_dict.values():
            prob_sum = prob_sum + v[1]
        # if there is zero chance of winning, calc static loosing probs and select card with highest loosing prob
        if prob_sum == 0:
            interval = 0
            for card in probs_dict.keys():
                if card.suit == trick.trump_suit:
                    prob = 1 - card.win_prob_trump
                else:
                    prob = 1 - card.win_prob
                probs_dict[card] = (interval, interval + prob)
                interval = interval + prob
        """
        for card in legal_cards:
            if has_highest_card:
                # calculate the dynamic probability to win if there is a chance for winning
                prob = card.calc_dynamic_win_prob(trick, played_cards, legal_cards, current_hand, players)
                if prob == 0.0 and card.rank == Rank.JESTER:
                    prob = 1 - card.win_prob
            else:
                # if no chance of winning, use a-priori win probabilities to calculate loose probability
                # so that 'bad' cards are played more likely
                if card.suit == trick.trump_suit:
                    prob = 1 - card.win_prob_trump
                else:
                    prob = 1 - card.win_prob
            probs_dict[card] = (interval, interval + prob)
            interval = interval + prob
        """
        rnd = random.uniform(0, interval)
        # get the corresponding card into which rnd falls from probs_dict
        for k, v in probs_dict.items():
            if v[0] <= rnd < v[1]:
                selected_card = k
                break

        if selected_card is None:
            raise Exception('No card selected. A card must be selected. Exiting.')
        return selected_card

    def select_suit(self):
        cards_without_joker = []
        for card in self.current_hand:
            if card.suit is not Suit.JOKER:
                cards_without_joker.append(card)

        if len(cards_without_joker) == 0:
            rnd_idx = random.randint(1, len(Suit) - 1)
            selected_suit = Suit(rnd_idx)
        else:
            rnd_idx = random.randint(0, len(cards_without_joker)-1)
            selected_suit = cards_without_joker[rnd_idx].suit

        return selected_suit
