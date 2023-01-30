import statistics
from collections import deque

from simulation import Simulation
from card import Card
from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_myopic import PlayerComputerMyopic
from state import State


class PlayerComputerRollout(PlayerComputerMyopic):

    def calculate_bid(self, state):
        pos_rollout_player_deal = -1
        pos_rollout_player_bid = -1
        pos_rollout_player_play = -1
        pos_humans_deal = -1
        pos_humans_bid = -1
        pos_humans_play = -1
        for i in range(0, len(state.players_deal_order)):
            if self == state.players_deal_order[i]:
                pos_rollout_player_deal = i
            if self == state.players_bid_order[i]:
                pos_rollout_player_bid = i
            if self == state.players_play_order[i]:
                pos_rollout_player_play = i
            if state.players_deal_order[i].player_type == 'human':
                pos_humans_deal = i
            if state.players_bid_order[i].player_type == 'human':
                pos_humans_bid = i
            if state.players_play_order[i].player_type == 'human':
                pos_humans_play = i

        bid_avg_score_dict = {}
        #bid_stdev_score_dict = {}
        #bid_median_score_dict = {}
        for bid in range(0, state.round_nr+1):
            # simulate n times and store score
            bid_scores = []
            for i in range(0, 128, 1):
                # create copy of state
                state_rollout = State(state.players_deal_order, state.round_nr, state.trick, state.deck, state.bids, state.players_bid_order, state.players_play_order)

                # substitute human player in copied state
                human_substitute = PlayerComputerRollout.substitute_player(state.players_deal_order[pos_humans_deal], PlayerComputerMyopic(self.number, 'computer', 'human_substitute_rollout'))
                del state_rollout.players_deal_order[pos_humans_deal]
                state_rollout.players_deal_order.insert(pos_humans_deal, human_substitute)
                del state_rollout.players_bid_order[pos_humans_bid]
                state_rollout.players_bid_order.insert(pos_humans_bid, human_substitute)
                del state_rollout.players_play_order[pos_humans_play]
                state_rollout.players_play_order.insert(pos_humans_play, human_substitute)

                # substitute rollout player
                base_policy_player = PlayerComputerRollout.substitute_player(self, PlayerComputerMyopic(self.number, 'computer', 'myopic_rollout'))
                # set bid to evaluate
                base_policy_player.current_bid = bid
                # delete rollout player and insert base policy player
                del state_rollout.players_deal_order[pos_rollout_player_deal]
                state_rollout.players_deal_order.insert(pos_rollout_player_deal, base_policy_player)
                del state_rollout.players_bid_order[pos_rollout_player_bid]
                state_rollout.players_bid_order.insert(pos_rollout_player_bid, base_policy_player)
                del state_rollout.players_play_order[pos_rollout_player_play]
                state_rollout.players_play_order.insert(pos_rollout_player_play, base_policy_player)
                # Simulate
                bid_scores.append(Simulation.simulate_episode(state_rollout, base_policy_player))
            bid_avg_score_dict[bid] = statistics.mean(bid_scores)
            #bid_stdev_score_dict[bid] = statistics.stdev(bid_scores)
            #bid_median_score_dict[bid] = statistics.median(bid_scores)
        max_avg_bid = max(bid_avg_score_dict, key=bid_avg_score_dict.get)
        return max_avg_bid

    @staticmethod
    def substitute_player(player, substitute):
        substitute.current_bid = player.current_bid
        substitute.current_hand = list(player.current_hand)
        substitute.played_cards = deque(player.played_cards)
        return substitute
