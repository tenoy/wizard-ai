from collections import deque
from player_computer import PlayerComputer
from player_human import PlayerHuman
from policies.player_computer_dynamic_weighted_random import PlayerComputerDynamicWeightedRandom
from policies.player_computer_myopic import PlayerComputerMyopic
from policies.player_computer_random import PlayerComputerRandom
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from trick import Trick


class State:

    def __init__(self, players_deal_order, round_nr, trick, deck, bids, players_play_order=None, played_cards=None):
        # deal order list is used for the deep copy (necessary for rollout policy)
        self.players_deal_order = deque()
        player_to_player_copy_dict = {}
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
            player_to_player_copy_dict[player] = player_copy

        # bid and play order are shallow copies of deal order deep copy
        # for bid order, the queue is always rotated by -1
        self.players_bid_order = deque(self.players_deal_order)
        self.players_bid_order.rotate(-1)
        self.players_play_order = deque()
        # for play order, the queue is rotated by -2 if empty, else put the copies in the same order as in play_order list
        if players_play_order is None:
            self.players_play_order.extend(self.players_deal_order)
            self.players_play_order.rotate(-2)
        else:
            for player in players_play_order:
                player_copy = player_to_player_copy_dict[player]
                self.players_play_order.append(player_copy)

        self.round_nr = round_nr
        self.trick = Trick(trump_suit=trick.trump_suit, trump_card=trick.trump_card, leading_suit=trick.leading_suit, cards=list(trick.cards), played_by=list(), round_nr=round_nr, trick_nr=trick.trick_nr)
        for player in trick.played_by:
            player_copy = player_to_player_copy_dict[player]
            self.trick.played_by.append(player_copy)
        self.deck = list(deck)
        self.bids = dict(bids)
        if played_cards is not None:
            self.played_cards = list(played_cards)
        else:
            self.played_cards = list()
        self.tricks = []

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

