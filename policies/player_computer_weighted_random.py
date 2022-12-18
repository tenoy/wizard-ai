import random
from enum_suit import Suit
from player_computer import PlayerComputer


# static weighted random policy
# bids using a-priori winning probabilities of cards in hand
# plays cards in a similar way
class PlayerComputerWeightedRandom(PlayerComputer):

    def calculate_bid(self, round_nr=None, previous_bids=None, players=None, trump_suit=None):
        bid = 0
        for card in self.current_hand:
            rnd = random.uniform(0, 1)
            if card.suit == trump_suit or trump_suit is None:
                prob = card.win_prob_trump
            else:
                prob = card.win_prob
            if rnd <= prob:
                bid = bid + 1

        return bid

    def recalculate_bid(self, bid, round_nr=None, previous_bids=None, players=None, trump_suit=None):
        if bid == 0:
            bid = 1
        else:
            bid = bid + random.randint(-1, 1)
        return bid

    def select_card(self, trick, bids, legal_cards, current_hand, played_cards, number_of_players):
        # build 'probability intervals' whose size correspond to their 'probability'
        interval = 0
        probs_dict = {}
        # todo: in eigene methode "build_interval", damit der dynamic weighted random player es benutzen kann
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

    def select_suit(self):
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
