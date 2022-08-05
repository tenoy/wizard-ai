from abc import abstractmethod


class Player:
    def __init__(self, number, player_type):
        self.number = number
        # can be computer or human
        self.player_type = player_type
        self.current_hand = []
        self.current_bid = -1
        self.current_tricks_won = 0
        self.current_score = 0

        self.history_bids = []
        self.history_scores = []

        self.played_card = None

    @abstractmethod
    def make_bid(self, round_nr, previous_bids, players, trump_suit):
        pass

    def is_valid_bid(self, bid, round_nr, previous_bids, players):
        if len(previous_bids) == len(players) - 1:
            if sum(previous_bids) + bid == round_nr:
               return False
            else:
                return True
        else:
            return True

    def contains_current_hand_leading_suit(self, leading_suit):
        for card in self.current_hand:
            if card.suit == leading_suit:
                return True
        return False

    @abstractmethod
    def play(self, trick, leading_suit, trump_suit):
        pass

    def __str__(self):
        return 'Player: ' + str(self.number) + ', Score: ' + str(self.current_score)






