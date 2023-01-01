from abc import abstractmethod
from collections import deque
from enum_suit import Suit


class Player:
    number_player = 0

    def __init__(self, player_type):
        self.number = Player.number_player
        Player.number_player = Player.number_player + 1
        # can be computer or human
        self.player_type = player_type
        self.current_hand = []
        self.current_bid = -1
        self.current_tricks_won = 0
        self.current_score = 0
        self.games_won = 0

        self.history_bids = []
        self.history_scores = []

        self.played_cards = deque()

    def is_valid_bid(self, bid, round_nr, previous_bids, players):
        if bid < 0:
            return False
        if len(previous_bids) == len(players) - 1:
            if sum(previous_bids.values()) + bid == round_nr:
                return False
            else:
                return True
        else:
            return True

    def print_current_hand(self):
        print('Current hand:')
        for k in range(0, len(self.current_hand)):
            print('(' + str(k + 1) + ') ' + str(self.current_hand[k]) + ' ', end=' ')
        print('')

    def has_leading_suit_in_hand(self, leading_suit):
        for card in self.current_hand:
            if card.suit == leading_suit:
                return True
        return False

    def is_valid_card(self, selected_card, leading_suit):
        if leading_suit is None:
            return True
        elif leading_suit == Suit.JOKER:
            return True
        elif selected_card.suit == Suit.JOKER:
            return True
        else:
            if self.has_leading_suit_in_hand(self.current_hand, leading_suit):
                if selected_card.suit == leading_suit:
                    return True
                else:
                    return False
            else:
                return True

    @abstractmethod
    def make_bid(self, round_nr, previous_bids, players, trump_suit):
        pass

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def pick_suit(self):
        pass

    def __str__(self):
        return 'Player_' + str(self.number)

    def __repr__(self):
        return 'Player_' + str(self.number)

    @staticmethod
    def get_played_cards(players):
        played_cards = list()
        for player in players:
            played_cards.extend(player.played_cards)
        return played_cards






