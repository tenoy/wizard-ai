from __future__ import annotations
from abc import abstractmethod
from enum_rank import Rank
from enum_suit import Suit
from player import Player
from typing import TYPE_CHECKING, Union, Literal

if TYPE_CHECKING:
    from state import State
    from card import Card


class PlayerComputer(Player):

    def __init__(self, number: int, player_type: Literal["computer"], policy_name: str) -> None:
        super(PlayerComputer, self).__init__(number, player_type)
        self.policy = policy_name

    def make_bid(self, state: State) -> int:
        bid = self.calculate_bid(state)
        while not self.is_valid_bid(state=state, bid=bid):
            bid = self.recalculate_bid(state, bid)

        return bid

    def play(self, state: State) -> Card:
        legal_cards = self.get_legal_cards(state.trick.leading_suit)
        if len(legal_cards) == 1:
            return legal_cards[0]
        else:
            selected_card = self.select_card(state, legal_cards=legal_cards, played_cards=self.get_played_cards(state.players_play_order))

        if selected_card is None:
            raise Exception('No card selected. A card must be selected. Exiting.')

        self.played_cards.appendleft(selected_card)
        self.current_hand.remove(selected_card)
        return selected_card

    def pick_suit(self, state: State) -> Suit:
        selected_suit = self.select_suit(state)

        if selected_suit is None:
            raise Exception('No suit selected. A suit must be selected. Exiting.')
        return selected_suit

    @abstractmethod
    def select_card(self, state: State, legal_cards: list[Card], played_cards: list[Card]=None) -> Card:
        pass

    @abstractmethod
    def calculate_bid(self, state: State) -> int:
        pass

    @abstractmethod
    def recalculate_bid(self, state: State, bid: int) -> int:
        pass

    @abstractmethod
    def select_suit(self, state: State) -> Suit:
        pass

    def get_legal_cards(self, leading_suit: Suit) -> list[Card]:
        # prepare set of cards that are allowed to play so that the policies dont have to deal with that again and again
        legal_cards = []
        if leading_suit is None or leading_suit == Suit.JOKER or not self.has_leading_suit_in_hand(leading_suit):
            legal_cards.extend(self.current_hand)
        else:
            for card in self.current_hand:
                if card.suit == leading_suit or card.suit == Suit.JOKER:
                    legal_cards.append(card)
        return legal_cards

    def get_highest_legal_card(self, legal_cards: list, trump_suit: Suit, leading_suit: Suit) -> Union[Card, None]:
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


    def __str__(self):
        return 'Player_' + str(self.number) + ' ' + self.policy

    def __repr__(self):
        return 'Player_' + str(self.number) + ' ' + self.policy