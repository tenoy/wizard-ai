from __future__ import annotations
import random
from enum_suit import Suit
from player_computer import PlayerComputer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import State
    from card import Card


class PlayerComputerRandom(PlayerComputer):

    def calculate_bid(self, state: State) -> int:
        bid = random.randint(0, state.round_nr)
        return bid

    def recalculate_bid(self, state: State, bid: int) -> int:
        return self.calculate_bid(state)

    def select_card(self, state: State, legal_cards: list[Card], played_cards: list[Card]=None) -> Card:
        card_idx = random.randint(0, len(legal_cards)-1)
        selected_card = legal_cards[card_idx]
        return selected_card

    def select_suit(self, state: State) -> Suit:
        rnd_idx = random.randint(1, len(Suit)-1)
        selected_suit = Suit(rnd_idx)
        return selected_suit
