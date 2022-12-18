import random
from abc import abstractmethod

from enum_rank import Rank
from enum_suit import Suit
from player import Player
from policies.dynamic_weighted_random_policy import DynamicWeightedRandomPolicy
from policies.random_policy import RandomPolicy
from policies.weighted_random_policy import WeightedRandomPolicy


class PlayerComputer(Player):

    def __init__(self, number, player_type, policy):
        super(PlayerComputer, self).__init__(number, player_type)
        self.policy = policy

    def make_bid(self, round_nr, previous_bids, players, trump_suit):
        # sum of bids is not allowed to be equal to the number of the round

        bid = self.calculate_bid(round_nr, previous_bids, players, trump_suit)
        while not self.is_valid_bid(bid, round_nr, previous_bids, players):
            bid = self.recalculate_bid(bid, round_nr, previous_bids, players, trump_suit)

        """
        match self.policy:
            case 'random':
                bid = RandomPolicy.calculate_bid(round_nr)
                while not self.is_valid_bid(bid, round_nr, previous_bids, players):
                    bid = RandomPolicy.recalculate_bid(round_nr)
            case 'weighted_random':
                bid = WeightedRandomPolicy.calculate_bid(round_nr, self.current_hand, trump_suit)
                while not self.is_valid_bid(bid, round_nr, previous_bids, players):
                    bid = WeightedRandomPolicy.recalculate_bid(bid)
            case 'dynamic_weighted_random':
                bid = DynamicWeightedRandomPolicy.calculate_bid(round_nr, self.current_hand, trump_suit)
                while not self.is_valid_bid(bid, round_nr, previous_bids, players):
                    bid = DynamicWeightedRandomPolicy.recalculate_bid(bid)
        """
        return bid

    def play(self, trick, bids):
        legal_cards = self.get_legal_cards(trick.leading_suit)
        selected_card = self.select_card(trick, bids, legal_cards, self.current_hand, self.get_played_cards(bids.keys()), bids.keys())
        """
        match self.policy:
            case 'random':
                selected_card = RandomPolicy.select_card(legal_cards)
            case 'weighted_random':
                selected_card = WeightedRandomPolicy.select_card(trick, legal_cards)
            case 'dynamic_weighted_random':
                selected_card = DynamicWeightedRandomPolicy.select_card(trick, bids, legal_cards, self.current_hand, self.get_played_cards(bids.keys()), bids.keys())
        """
        if selected_card is None:
            raise Exception('No card selected. A card must be selected. Exiting.')

        self.played_cards.appendleft(selected_card)
        self.current_hand.remove(selected_card)
        return selected_card

    def pick_suit(self):
        selected_suit = self.select_suit()
        """
        match self.policy:
            case 'random':
                selected_suit = RandomPolicy.select_suit()
            case 'weighted_random':
                selected_suit = WeightedRandomPolicy.select_suit(self.current_hand)
            case 'dynamic_weighted_random':
                selected_suit = DynamicWeightedRandomPolicy.select_suit(self.current_hand)
        """
        if selected_suit is None:
            raise Exception('No suit selected. A suit must be selected. Exiting.')
        return selected_suit

    @abstractmethod
    def select_card(self):
        pass

    @abstractmethod
    def calculate_bid(self):
        pass

    @abstractmethod
    def recalculate_bid(self):
        pass

    @abstractmethod
    def select_suit(self):
        pass

    def get_legal_cards(self, leading_suit):
        # prepare set of cards that are allowed to play so that the policies dont have to deal with that again and again
        legal_cards = []
        if leading_suit is None or leading_suit == Suit.JOKER or not self.has_leading_suit_in_hand(leading_suit):
            legal_cards.extend(self.current_hand)
        else:
            for card in self.current_hand:
                if card.suit == leading_suit or card.suit == Suit.JOKER:
                    legal_cards.append(card)
        return legal_cards

    def get_highest_legal_card(self, legal_cards, trump_suit, leading_suit):
        # case with empty legal cards
        if len(legal_cards) == 0:
            return None

        # case with wizard in legal cards
        for card in legal_cards:
            if card.rank == Rank.WIZARD:
                return card

        # case with trump in legal cards -> get highest trump card
        if trump_suit is not None:
            trump_cards = []
            for card in legal_cards:
                if card.suit == trump_suit:
                    trump_cards.append(card)

            if len(trump_cards) == 1:
                return trump_cards[0]
            elif len(trump_cards) > 1:
                return max(trump_cards)

        # case without wizard or trump card
        leading_suit_cards = []
        if leading_suit is not None and leading_suit != Suit.JOKER:
            for card in legal_cards:
                if card.suit == leading_suit:
                    leading_suit_cards.append(card)

            if len(leading_suit_cards) == 1:
                return leading_suit_cards[0]
            elif len(leading_suit_cards) > 1:
                return max(leading_suit_cards)
            else:
                return max(legal_cards)
        else:
            # case where no leading suit is in trick or leading suit is a joker card
            return max(legal_cards)

