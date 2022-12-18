from math import comb

from enum_rank import Rank
from enum_suit import Suit


class Card:

    def __init__(self, suit, rank, instance_number=0):
        self.suit = suit
        self.rank = rank
        # wizard and jester exist 4 times, to distinguish them an instance number from 1 to 4 is used
        # all other cards exit only 1 time and have instance number 0
        self.instance_number = instance_number
        self.win_prob = self.calc_static_win_prob('normal')
        self.win_prob_trump = self.calc_static_win_prob('trump')

    # use only to compare cards of same suit!
    def __gt__(self, other):
        return self.rank > other.rank

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit and self.instance_number == other.instance_number

    def __hash__(self) -> int:
        return super().__hash__()

    def __str__(self):
        return str(self.rank) + ' ' + str(self.suit)

    def __repr__(self):
        return str(self.rank) + ' ' + str(self.suit)

    # Calculates static a-priori probability for this card being the winning card
    # Therefore the (counter)probability of drawing a higher card is calculated
    # Used for bidding phase
    def calc_static_win_prob(self, suit_type):
        if self.rank == Rank.WIZARD:
            return 1 - 3/59
        if self.rank == Rank.JESTER:
            return 1 - 56/59
        # if type of suit is normal -> card is not trump, but may be leading suit
        num_of_cards_higher = Rank.ACE - self.rank
        if suit_type == 'normal':
            # In 25% of the cases the card will match the leading suit
            # Higher cards: Wizards (4), trump cards (len(Rank)-2) and higher rank leading suit cards (num_of_cards_higher)
            leading_suit_prob = (4 + len(Rank)-2 + num_of_cards_higher) / 59
            # In 75% of the cases the card will not match the leading suit
            # All other cards are considered higher except the own suit and jester
            not_leading_suit_prob = (4 + (len(Rank)-2)*3 + num_of_cards_higher) / 59
            prob = 0.25 * leading_suit_prob + 0.75 * not_leading_suit_prob
            # num_of_cards_higher = num_of_cards_higher * (len(Suit)-2) + (len(Rank)-2) * 2 + 4
        # if type of suit is trump, then count only higher trump cards and wizards
        if suit_type == 'trump':
            num_of_cards_higher = num_of_cards_higher + 4
            prob = num_of_cards_higher / 59

        win_prob = 1 - prob
        return win_prob

    # Calculates the dynamic / state dependent winning probability of a card
    def calc_dynamic_win_prob(self, trick, cards_played, cards_legal, cards_hand, players):
        # calc how many turns are made after playing this card
        n_players = len(players)
        n_cards_played = len(cards_played)
        n_cards_hand = len(cards_hand)
        n_turns_left_in_trick = n_players - len(trick.cards) - 1
        n_cards_drawable = 60 - n_cards_played - n_cards_hand

        # case if this card is a wizard
        if self.rank == Rank.WIZARD:
            # if there is a wizard in trick already then there is no chance of winning, else it is a 100% win
            if len([card for card in trick.cards if card.rank == Rank.WIZARD]):
                return 0
            else:
                return 1

        # case if this card is a jester
        if self.rank == Rank.JESTER:
            # a jester can only win a trick if all following cards are also jesters (which is only possible up to 4 players)
            if len(trick.cards) == 0 and n_players <= 4:
                jesters_played = [card for card in cards_played if card.rank == Rank.JESTER]
                jesters_in_hand = [card for card in cards_legal if card.rank == Rank.JESTER]
                n_jesters_drawable = 4 - len(jesters_played) - len(jesters_in_hand)
                prob = self.calc_hypergeometric_prob(M=n_jesters_drawable, k=n_turns_left_in_trick, N=n_cards_drawable, n=n_turns_left_in_trick)
                return prob
            else:
                return 0

        # case if this is a trump suit card (and may be also a leading suit card)
        if self.suit == trick.trump_suit:
            # case if trick contains a higher trump card
            if len([card for card in trick.cards if card.suit == trick.trump_suit and card.rank > self.rank]) > 0:
                return 0
            else:
                # get all higher cards (trumps and wizards) that have been played
                higher_cards_played = [card for card in cards_played if (card.suit == trick.trump_suit or card.suit == Suit.JOKER) and card.rank > self.rank]
                # get all higher cards (trumps and wizards) in hand that are allowed to play
                higher_cards_hand = [card for card in cards_legal if (card.suit == trick.trump_suit or card.suit == Suit.JOKER) and card.rank > self.rank]
                n_higher_cards = 4 + Rank.ACE - self.rank - len(higher_cards_played) - len(higher_cards_hand)
                # get probability that 0 higher cards are played -> that is the win prob of this card
                prob = self.calc_hypergeometric_prob(M=n_higher_cards, k=0, N=n_cards_drawable, n=n_turns_left_in_trick)
                return prob

        # case this card is a leading suit card (but not a trump suit card, this case is covered above)
        leading_suit = trick.get_leading_suit()
        # if leading suit is none then this card will be the leading suit
        if leading_suit is None:
            leading_suit = self.suit
        if self.suit == leading_suit:
            # case if trick contains a trump card or a higher leading suit card
            if len([card for card in trick.cards if card.suit == trick.trump_suit or (card.suit == leading_suit and card.rank > self.rank)]) > 0:
                return 0
            else:
                # get all higher cards (leading suits, trumps, wizards) that have been played
                higher_cards_played = [card for card in cards_played if(card.suit == Suit.JOKER or card.suit == leading_suit) and card.rank > self.rank or card.suit == trick.trump_suit]
                # get all higher cards (leading suits, trumps and wizards) in hand that are allowed to play
                higher_cards_hand = [card for card in cards_legal if (card.suit == Suit.JOKER or card.suit == leading_suit) and card.rank > self.rank or card.suit == trick.trump_suit]
                # if jester is drawn as trump card, then there is no trump suit
                if trick.trump_suit is None:
                    n_trump_cards = 0
                else:
                    n_trump_cards = 13
                n_higher_cards = 4 + Rank.ACE - self.rank + n_trump_cards - len(higher_cards_played) - len(higher_cards_hand)
                prob = self.calc_hypergeometric_prob(M=n_higher_cards, k=0, N=n_cards_drawable, n=n_turns_left_in_trick)
                return prob

        # case this card is a "normal" card -> this means the suit does not match the leading suit and thus 0% chance of winning
        if self.suit != leading_suit:
            return 0

    # Probability that a card wins is the probability that no higher card is drawn afterwards
    # Use hypergeometric distribution formula: P(X=k) = ((M over k) * (N - M over n - k)) / (N over n)
    # N = number of cards drawable, M = Number of higher cards, n = turns left in trick, k = exact number of times a card should be drawn
    # Example for winning with a jester in a 3 player game:
    # N=59 (no cards played yet),  M=3 (3 Jesters left in deck), n=2 (2 turns to play), k=2 (both must play jester)
    # Example for ACE HEARTS trump card in a 3 player game:
    # N=59, M=4 (only the wizards can beat a trump ace), n=2 (2 turns to play), k=0 (both must NOT play a wizard)
    # https://studyflix.de/statistik/ziehen-ohne-zuruecklegen-1077
    def calc_hypergeometric_prob(self, M: int, k: int, N: int, n: int) -> float:
        prob = comb(M, k) * comb(N - M, n - k) / comb(N, n)
        return prob
