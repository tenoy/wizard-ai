from __future__ import annotations
from abc import abstractmethod
from collections import deque
from enum_suit import Suit
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from state import State
    from card import Card


class Player:

    def __init__(self, number: int, player_type: Literal["computer", "human"]) -> None:
        self.number = number
        # can be computer or human
        self.player_type = player_type
        self.current_hand = []
        self.current_bid = -1
        self.current_card_idx = -1
        self.current_tricks_won = 0
        self.current_score = 0
        self.games_won = 0

        self.history_bids = []
        self.history_scores = []

        self.played_cards = deque()

    @staticmethod
    def is_valid_bid(state: State, bid: int) -> bool:
        if bid < 0:
            return False
        if len(state.bids) == len(state.players_deal_order) - 1:
            if sum(state.bids.values()) + bid == state.round_nr:
                return False
            else:
                return True
        else:
            return True

    def print_current_hand(self) -> None:
        print('Current hand:')
        for k in range(0, len(self.current_hand)):
            print('(' + str(k + 1) + ') ' + str(self.current_hand[k]) + ' ', end=' ')
        print('')

    def has_leading_suit_in_hand(self, leading_suit: Suit) -> bool:
        for card in self.current_hand:
            if card.suit == leading_suit:
                return True
        return False

    def is_valid_card(self, selected_card: Card, leading_suit: Suit) -> bool:
        if leading_suit is None:
            return True
        elif leading_suit == Suit.JOKER:
            return True
        elif selected_card.suit == Suit.JOKER:
            return True
        else:
            if self.has_leading_suit_in_hand(leading_suit):
                if selected_card.suit == leading_suit:
                    return True
                else:
                    return False
            else:
                return True

    @abstractmethod
    def make_bid(self, state: State) -> int:
        pass

    @abstractmethod
    def play(self, state: State) -> Card:
        pass

    @abstractmethod
    def pick_suit(self, state: State) -> Suit:
        pass

    def __str__(self) -> str:
        return 'Player_' + str(self.number)

    def __repr__(self) -> str:
        return 'Player_' + str(self.number)

    @staticmethod
    def get_played_cards(players: list[Player]) -> list[Card]:
        played_cards = list()
        for player in players:
            played_cards.extend(player.played_cards)
        return played_cards






