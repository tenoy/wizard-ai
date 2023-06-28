from __future__ import annotations
from collections import deque
from player_computer import PlayerComputer
from player_human import PlayerHuman
from policies.player_computer_dynamic_weighted_random import PlayerComputerDynamicWeightedRandom
from policies.player_computer_myopic import PlayerComputerMyopic
from policies.player_computer_random import PlayerComputerRandom
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from trick import Trick
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from card import Card
    from player import Player


class State:

    def __init__(self, players_deal_order: deque[Player], players_bid_order: deque[Player], players_play_order: deque[Player], round_nr: int, trick: Trick, deck: list[Card], bids: dict[Player, int], played_cards: list[Card]=None) -> None:
        self.players_deal_order = players_deal_order
        self.players_bid_order = players_bid_order
        self.players_play_order = players_play_order
        self.round_nr = round_nr
        self.trick = trick
        self.deck = deck
        self.bids = bids
        self.played_cards = played_cards
        self.tricks = []

    def copy_state(self) -> State:
        # players_deal_order, round_nr, trick, deck, bids, players_play_order=None, played_cards=None
        state_copy = State(self.players_deal_order, self.players_bid_order, self.players_play_order, self.round_nr, self.trick, self.deck, self.bids)
        # deal order list is used for the deep copy (necessary for rollout policy)
        state_copy.players_deal_order = deque()
        player_to_player_copy_dict = {}
        for player in self.players_deal_order:
            # player_copy = copy.deepcopy(player)
            # self.players_deal_order.append(player_copy)
            player_copy = State.get_player_class(player)
            player_copy.current_hand = list(player.current_hand)
            player_copy.current_bid = player.current_bid
            player_copy.current_tricks_won = player.current_tricks_won
            player_copy.current_score = player.current_score
            player_copy.played_cards = deque(player.played_cards)
            state_copy.players_deal_order.append(player_copy)
            player_to_player_copy_dict[player] = player_copy

        # bid and play order are shallow copies of deal order deep copy
        # for bid order, the queue is always rotated by -1
        state_copy.players_bid_order = deque(state_copy.players_deal_order)
        state_copy.players_bid_order.rotate(-1)
        state_copy.players_play_order = deque()
        # for play order, the queue is rotated by -2 if empty, else put the copies in the same order as in play_order list
        if self.players_play_order is None:
            state_copy.players_play_order.extend(state_copy.players_deal_order)
            state_copy.players_play_order.rotate(-2)
        else:
            for player in self.players_play_order:
                player_copy = player_to_player_copy_dict[player]
                state_copy.players_play_order.append(player_copy)

        state_copy.round_nr = self.round_nr
        state_copy.trick = Trick(trump_suit=self.trick.trump_suit, trump_card=self.trick.trump_card, leading_suit=self.trick.leading_suit,
                           cards=list(self.trick.cards), played_by=list(), round_nr=self.round_nr, trick_nr=self.trick.trick_nr)
        for player in self.trick.played_by:
            player_copy = player_to_player_copy_dict[player]
            state_copy.trick.played_by.append(player_copy)
        state_copy.deck = list(self.deck)
        state_copy.bids = dict(self.bids)

        if self.played_cards is not None:
            state_copy.played_cards = list(self.played_cards)
        else:
            state_copy.played_cards = list()
        state_copy.tricks = []
        return state_copy

    @staticmethod
    def get_player_class(player: Player) -> Player:
        # local import necessary or else a circular import error is happening
        from policies.player_computer_rollout import PlayerComputerRollout
        if isinstance(player, PlayerComputerRandom):
            return PlayerComputerRandom(player.number, player.player_type, player.policy)
        elif isinstance(player, PlayerComputerRollout):
            return PlayerComputerRollout(player.number, player.player_type, player.policy)
        elif isinstance(player, PlayerComputerMyopic):
            return PlayerComputerMyopic(player.number, player.player_type, player.policy)
        elif isinstance(player, PlayerComputerDynamicWeightedRandom):
            return PlayerComputerDynamicWeightedRandom(player.number, player.player_type, player.policy)
        elif isinstance(player, PlayerComputerWeightedRandom):
            return PlayerComputerWeightedRandom(player.number, player.player_type, player.policy)
        elif isinstance(player, PlayerHuman):
            return PlayerHuman(player.number, player.player_type, player_name=player.name, input_q=player.input_q, output_q=player.output_q)
        else:
            return PlayerComputer(player.number, player.player_type, player.policy)

