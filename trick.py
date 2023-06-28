from __future__ import annotations
from enum_rank import Rank
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import State
    from card import Card
    from player import Player
    from enum_suit import Suit


class Trick:

    def __init__(self, trump_card: Card=None, trump_suit: Suit=None, leading_suit: Suit=None, cards: list[Card]=None, played_by: list[Player]=None, round_nr: int=None, trick_nr: int=None) -> None:
        self.trump_card = trump_card
        self.trump_suit = trump_suit
        self.leading_suit = leading_suit
        self.cards = cards
        self.played_by = played_by
        self.round_nr = round_nr
        self.trick_nr = trick_nr

    def add_card(self, card: Card, player: Player) -> None:
        self.cards.append(card)
        self.played_by.append(player)

    def get_highest_trick_card_index(self) -> int | None:
        # case with empty trick
        if len(self.cards) == 0:
            return None
        # case with wizard in trick -> first wizard wins
        for idx in range(0, len(self.cards)):
            card = self.cards[idx]
            if card.rank == Rank.WIZARD:
                return idx

        # case with trump in trick -> the highest trump card wins
        if self.trump_suit is not None:
            trump_cards = {}
            for idx in range(0, len(self.cards)):
                card = self.cards[idx]
                if card.suit == self.trump_suit:
                    trump_cards[card] = idx

            if len(trump_cards) > 0:
                highest_trump = max(trump_cards)
                return trump_cards[highest_trump]

        # case without wizard or trump card
        if self.leading_suit is None:
            self.leading_suit = self.get_leading_suit()

        leading_suit_cards = {}
        # leading suit might still be None (if only jesters are played)
        if self.leading_suit is not None:
            for idx in range(0, len(self.cards)):
                card = self.cards[idx]
                if card.suit == self.leading_suit:
                    leading_suit_cards[card] = idx

            if len(leading_suit_cards) > 0:
                highest_leading_suit = max(leading_suit_cards)
                return leading_suit_cards[highest_leading_suit]

        else:
            # case with only jesters
            return 0  # the first jester wins

    def get_leading_suit(self) -> Suit | None:
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

    def __repr__(self) -> str:
        return 'Trump: ' + str(self.trump_suit) + ' ' + str(self.cards) + ' ' + str(self.played_by)