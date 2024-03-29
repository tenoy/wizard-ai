from __future__ import annotations

from collections import deque
from math import comb
from PIL import Image
from enum_rank import Rank
from enum_suit import Suit
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import State
    from card import Card
    from player import Player
    from trick import Trick


class Card:

    def __init__(self, suit: Suit, rank: Rank, instance_number: int=0, is_game_mode: bool=False) -> None:
        self.suit = suit
        self.rank = rank
        # wizard and jester exist 4 times, to distinguish each instance a number from 1 to 4 is given
        # all other cards exit only one time and have instance number of 0
        self.instance_number = instance_number
        # self.win_prob = self.calc_static_win_prob('normal')
        # self.win_prob_trump = self.calc_static_win_prob('trump')
        # load a card image if program is started in game mode
        if is_game_mode:
            # call image reading and resizing method
            self.card_image = self.load_card_image()
        else:
            self.card_image = None

    def load_card_image(self) -> Image:
        if self.suit != Suit.JOKER:
            suit_lowercase = str(self.suit).lower()
            image_original = Image.open(f'gui/cards/{self.rank.value}_of_{suit_lowercase}.png')
        else:
            rank_lowercase = str(self.rank).lower()
            image_original = Image.open(f'gui/cards/{rank_lowercase}.png')
        card_image = image_original.resize((100, 145))
        # card_image = ImageTk.PhotoImage(image_resize)
        return card_image

    # use only to compare cards of same suit!
    def __gt__(self, other: Card) -> bool:
        return self.rank > other.rank

    def __eq__(self, other: Card) -> bool:
        return self.rank == other.rank and self.suit == other.suit and self.instance_number == other.instance_number

    def __hash__(self) -> int:
        return super().__hash__()

    def __str__(self) -> str:
        return str(self.rank) + ' ' + str(self.suit)

    def __repr__(self) -> str:
        return str(self.rank) + ' ' + str(self.suit)

    # Calculates static a-priori probability for this card being the winning card
    # Therefore the (counter)probability of drawing a higher card is calculated
    # Used mostly in bidding phase since only current hand and trump card is known
    def calc_static_win_prob(self, trick: Trick, current_hand: list[Card], players: deque[Player], player: Player) -> float:
        pos = -1
        for i in range(0, len(players)):
            if players[i] == player:
                pos = i
                break

        if trick.trump_card is None:
            n_trump_card = 0
            n_trump_wizard = 0
        else:
            n_trump_card = 1
            if trick.trump_card.rank == Rank.WIZARD:
                n_trump_wizard = 1
            else:
                n_trump_wizard = 0

        n_cards_hand = len(current_hand)
        n_players = len(players)
        # the trump card is also not drawable (except in last round)
        n_cards_drawable = 60 - n_cards_hand - n_trump_card

        if self.rank == Rank.WIZARD:
            n_wizards_in_hand = len([card for card in current_hand if card.rank == Rank.WIZARD])
            n_wizards_drawable = 4 - n_trump_wizard - n_wizards_in_hand
            # to determine the correct number of possible wizards before own turn, get minimum of own position and wizards drawable
            n_wizards_before = min(pos, n_wizards_drawable)
            # get probability that 0 wizard cards are played before own wizard
            prob = self.calc_hypergeometric_prob(M=n_wizards_before, k=0, N=n_cards_drawable, n=n_players-1)
            return prob

        if self.rank == Rank.JESTER:
            if n_players > 4:
                prob = 0
            else:
                n_jesters_in_hand = len([card for card in current_hand if card.rank == Rank.JESTER])
                # it is not possible to win in all possible constellations of number of players and number of jesters in hand if the sum is above 5
                # if e.g. 2 jesters are in the current hand and the number of players is 4, then its not possible to win
                if n_jesters_in_hand + n_players > 5:
                    prob = 0
                else:
                    n_jesters_drawable = 4 - n_jesters_in_hand
                    prob = self.calc_hypergeometric_prob(M=n_jesters_drawable, k=n_players-1, N=n_cards_drawable, n=n_players-1)
            return prob

        # if type of suit is trump, then count only higher trump cards and wizards
        # get all higher cards (trumps and wizards) in hand that are allowed to play
        if self.suit == trick.trump_suit:
            # if the trump card is higher (but not wizard), it also must be subtracted for the number of higher cards
            # note that the trump suit of the trick can be different from the trump suit of the trump card (if wizard or jester)
            if trick.trump_card.rank > self.rank and trick.trump_card.suit != Suit.JOKER:
                higher_trump_card = 1
            else:
                higher_trump_card = 0
            n_higher_cards_hand = len([card for card in current_hand if(card.suit == trick.trump_suit or card.suit == Suit.JOKER) and card.rank > self.rank])
            n_higher_cards = 4 - n_trump_wizard + Rank.ACE - self.rank - n_higher_cards_hand - higher_trump_card
            # get probability that 0 higher cards are played -> that is the win prob of this card
            prob = self.calc_hypergeometric_prob(M=n_higher_cards, k=0, N=n_cards_drawable, n=n_players-1)
            return prob

        else:
            # get all higher cards (leading suits, trumps and wizards) in hand that are allowed to play
            n_higher_cards_hand = len([card for card in current_hand if card.suit == Suit.JOKER and card.rank > self.rank or card.suit == trick.trump_suit])
            # in last round, no trump suit is available
            if trick.trump_suit is None:
                n_trump_cards = 0
            else:
                if trick.trump_card.rank == Rank.WIZARD:
                    n_trump_cards = 13 #no trump card is drawn from drawable
                else:
                    n_trump_cards = 12 #one less trump card since it was drawn for the trump card
            # In 25% of the cases the card will match the leading suit
            n_higher_cards = 4 - n_trump_wizard + Rank.ACE - self.rank + n_trump_cards - n_higher_cards_hand
            prob_leading_suit = self.calc_hypergeometric_prob(M=n_higher_cards, k=0, N=n_cards_drawable, n=n_players-1)
            # In 75% of the cases the card will not match the leading suit
            # If there is no trump suit get all higher card of the other suits
            if trick.trump_suit is None:
                factor = 3
            else:
                factor = 2
            n_higher_cards = 4 + factor*(Rank.ACE - self.rank) + n_trump_cards - n_higher_cards_hand
            prob_normal_card = self.calc_hypergeometric_prob(M=n_higher_cards, k=0, N=n_cards_drawable, n=n_players - 1)
            prob = 0.25 * prob_leading_suit + 0.75 * prob_normal_card
            return prob

    # Calculates the dynamic / state dependent winning probability of a card
    def calc_dynamic_win_prob(self, trick: Trick, cards_played: list[Card], cards_legal: list[Card], current_hand: list[Card], players: deque[Player]) -> float:
        # calc how many turns are made after playing this card
        n_players = len(players)
        n_cards_played = len(cards_played)
        n_cards_hand = len(current_hand)
        n_turns_left_in_trick = n_players - len(trick.cards) - 1

        if trick.trump_card is None:
            n_trump_card = 0
            n_trump_wizard = 0
        else:
            n_trump_card = 1
            if trick.trump_card.rank == Rank.WIZARD:
                n_trump_wizard = 1
            else:
                n_trump_wizard = 0

        n_cards_drawable = 60 - n_cards_played - n_cards_hand - n_trump_card

        # case if trick already contains wizard(s)
        if len([card for card in trick.cards if card.rank == Rank.WIZARD]) > 0:
            return 0

        # case if this card is a wizard (and no other wizards are in the trick)
        if self.rank == Rank.WIZARD:
            return 1

        # case if this card is a jester
        if self.rank == Rank.JESTER:
            # a jester can only win a trick if all following cards are also jesters (which is only possible up to 4 players)
            if len(trick.cards) == 0 and n_players <= 4:
                if trick.trump_card is None:
                    n_jester_trump_card = 0
                else:
                    if trick.trump_card.rank == Rank.JESTER:
                        n_jester_trump_card = 1
                    else:
                        n_jester_trump_card = 0
                jesters_played = [card for card in cards_played if card.rank == Rank.JESTER]
                jesters_in_hand = [card for card in cards_legal if card.rank == Rank.JESTER]
                n_jesters_drawable = 4 - len(jesters_played) - len(jesters_in_hand) - n_jester_trump_card
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
                # if the trump card is higher (but not wizard), it also must be accounted for the number of higher cards
                if trick.trump_card.rank > self.rank and trick.trump_card.suit != Suit.JOKER:
                    higher_trump_card = 1
                else:
                    higher_trump_card = 0

                # get all higher cards (trumps and wizards) that have been played in previous rounds
                higher_cards_played = [card for card in cards_played if (card.suit == trick.trump_suit or card.suit == Suit.JOKER) and card.rank > self.rank]
                # get all higher cards (trumps and wizards) in hand that are allowed to play
                higher_cards_hand = [card for card in cards_legal if (card.suit == trick.trump_suit or card.suit == Suit.JOKER) and card.rank > self.rank]
                n_higher_cards = 4 - n_trump_wizard + Rank.ACE - self.rank - len(higher_cards_played) - len(higher_cards_hand) - higher_trump_card
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
                    if trick.trump_card.rank == Rank.WIZARD:
                        n_trump_cards = 13
                    else:
                        n_trump_cards = 12
                n_higher_cards = 4 - n_trump_wizard + Rank.ACE - self.rank + n_trump_cards - len(higher_cards_played) - len(higher_cards_hand)
                prob = self.calc_hypergeometric_prob(M=n_higher_cards, k=0, N=n_cards_drawable, n=n_turns_left_in_trick)
                return prob

        # case this card is a "normal" card -> this means the suit does not match the leading suit and thus 0% chance of winning
        if self.suit != leading_suit:
            return 0

    # Probability that a card wins is the probability that no higher card is drawn afterwards
    # Use hypergeometric distribution formula: P(X=k) = ((M over k) * (N - M over n - k)) / (N over n)
    # N = number of cards drawable, M = Number of higher cards, n = turns left in trick, k = exact number of times a card should be drawn
    # Example arguments for winning prob with a jester in a 3 player game (when first to play):
    # N=58 (no cards played yet),  M=3 (3 Jesters left in deck), n=2 (2 turns to play), k=2 (both must play jester)
    # Example arguments for winning prob with a ACE HEARTS trump card in a 3 player game (when first to play):
    # N=58, M=4 (only the wizards can beat a trump ace), n=2 (2 turns to play), k=0 (both must NOT play a wizard)
    # https://studyflix.de/statistik/ziehen-ohne-zuruecklegen-1077
    @staticmethod
    def calc_hypergeometric_prob(M: int, k: int, N: int, n: int) -> float:
        if M < 0 or k < 0 or N < 0 or n < 0:
            print(f'M={M}, k={k}, N={N}, n={n}')
        prob = comb(M, k) * comb(N - M, n - k) / comb(N, n)
        return prob
