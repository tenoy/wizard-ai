from enum_rank import Rank
from enum_suit import Suit
from utils import get_leading_suit


class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.win_prob = self.calc_static_win_prob('normal')
        self.win_prob_trump = self.calc_static_win_prob('trump')

    # use only to compare cards of same suit!
    def __gt__(self, other):
        return self.rank > other.rank

    def __str__(self):
        return str(self.rank) + ' ' + str(self.suit)

    def __repr__(self):
        return str(self.rank) + ' ' + str(self.suit)

    # Calculates static a-priori probability for this card being the highest card drawn
    # Used for bidding phase
    def calc_static_win_prob(self, suit_type):
        if self.rank == Rank.WIZARD:
            return 1 - 3/59
        if self.rank == Rank.JESTER:
            return 1 - 56/59
        # if type of suit is normal -> card is not trump, but may be leading suit
        num_of_cards_higher = Rank.ACE - self.rank
        if suit_type is 'normal':
            # In 25% of the cases the card will match the leading suit
            # Wizards, trump cards and higher leading suit cards are higher
            leading_suit_prob = (4 + len(Rank)-2 + num_of_cards_higher) / 59
            # In 75% of the cases the card will not match
            # All other cards are considered higher except the own suit and jester
            not_leading_suit_prob = (4 + (len(Rank)-2)*3 + num_of_cards_higher) / 59
            prob = 0.25 * leading_suit_prob + 0.75 * not_leading_suit_prob
            #num_of_cards_higher = num_of_cards_higher * (len(Suit)-2) + (len(Rank)-2) * 2 + 4
        # if type of suit is trump, then count only higher trump cards and wizards
        if suit_type is 'trump':
            num_of_cards_higher = num_of_cards_higher + 4
            prob = num_of_cards_higher / 59

        win_prob = 1 - prob
        return win_prob

    def calc_dynamic_win_prob(self, suit_type, trick_cards, trump_suit):
        leading_suit = get_leading_suit(trick_cards)
        # card will be leading suit (if not jester)
        if leading_suit is None:
            # todo: calc prob of winning with leading suit
            print('diesdas')



