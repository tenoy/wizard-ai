import copy
from collections import deque

from player import Player
from player_computer import PlayerComputer
from player_human import PlayerHuman
from policies.player_computer_dynamic_weighted_random import PlayerComputerDynamicWeightedRandom
from policies.player_computer_myopic import PlayerComputerMyopic
from policies.player_computer_random import PlayerComputerRandom
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from trick import Trick


class State:

    def __init__(self, players_deal_order, round_nr, trick, deck, bids, players_bid_order=None, players_play_order=None, rotate_players_play_order=-2):
        # deal order list is used for the deep copy (necessary for rollout policy)
        self.players_deal_order = deque()
        for player in players_deal_order:
            # player_copy = copy.deepcopy(player)
            # self.players_deal_order.append(player_copy)
            player_copy = State.get_player_class(player)
            player_copy.current_hand = list(player.current_hand)
            player_copy.current_bid = player.current_bid
            player_copy.current_tricks_won = player.current_tricks_won
            player_copy.current_score = player.current_score
            player_copy.played_cards = deque(player.played_cards)
            self.players_deal_order.append(player_copy)
        # bid and play order are shallow copies of deal order deep copy
        self.players_bid_order = deque(self.players_deal_order)
        if players_bid_order is not None:
            self.players_bid_order.rotate(-1)
        self.players_play_order = deque(self.players_deal_order)
        if players_play_order is not None:
            self.players_play_order.rotate(rotate_players_play_order)
        self.round_nr = round_nr
        self.trick = Trick(trump_suit=trick.trump_suit, leading_suit=trick.leading_suit, cards=list(trick.cards), played_by=list(trick.played_by))
        self.deck = list(deck)
        self.bids = dict(bids)

    @staticmethod
    def get_player_class(player):
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

