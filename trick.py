from enum_rank import Rank


class Trick:

    def __init__(self, trump_card=None, trump_suit=None, leading_suit=None, cards=[], played_by=[], round_nr=None, trick_nr=None):
        self.trump_card = trump_card
        self.trump_suit = trump_suit
        self.leading_suit = leading_suit
        self.cards = cards
        self.played_by = played_by
        self.round_nr = round_nr
        self.trick_nr = trick_nr

    def add_card(self, card, player):
        self.cards.append(card)
        self.played_by.append(player)

    def get_highest_trick_card(self):
        # case with empty trick
        if len(self.cards) == 0:
            return None
        # case with wizard in trick -> first wizard wins
        for card in self.cards:
            if card.rank == Rank.WIZARD:
                return card
        # case with trump in trick -> the highest trump card wins
        if self.trump_suit is not None:
            trump_cards = []
            for card in self.cards:
                if card.suit == self.trump_suit:
                    trump_cards.append(card)

            if len(trump_cards) == 1:
                return trump_cards[0]
            elif len(trump_cards) > 1:
                return max(trump_cards)

        # case without wizard or trump card
        if self.leading_suit is None:
            self.leading_suit = self.get_leading_suit()

        leading_suit_cards = []
        # leading suit might still be None (if only jesters are played)
        if self.leading_suit is not None:
            for card in self.cards:
                if card.suit == self.leading_suit:
                    leading_suit_cards.append(card)

            if len(leading_suit_cards) == 1:
                return leading_suit_cards[0]
            else:
                return max(leading_suit_cards)
        else:
            # case with only jesters
            return self.cards[0]  # the first jester wins

    def get_leading_suit(self):
        leading_suit = None
        for card in self.cards:
            # if jester is played first, then the next card will be the leading suit,
            # except if it's also a jester
            if card.rank != Rank.JESTER:
                if card.rank == Rank.WIZARD:
                    return None
                leading_suit = card.suit
                return leading_suit
        return leading_suit

    def __repr__(self):
        return 'Trump: ' + str(self.trump_suit) + ' ' + str(self.cards) + ' ' + str(self.played_by)