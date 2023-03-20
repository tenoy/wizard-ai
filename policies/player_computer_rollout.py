import statistics
from collections import deque

from joblib import Parallel, delayed

from player_human import PlayerHuman
from simulation import Simulation
from policies.player_computer_myopic import PlayerComputerMyopic
from state import State


class PlayerComputerRollout(PlayerComputerMyopic):

    def calculate_bid(self, state):
        # the original state must be copied and manipulated so that no rollout / human player are in the rollout state
        state_rollout_template = PlayerComputerRollout.generate_template_rollout_state(state)
        # with Parallel(n_jobs=8) as parallel:
        bid_avg_score_dict = {}
        #bid_stdev_score_dict = {}
        #bid_median_score_dict = {}
        for bid in range(0, state.round_nr+1):
            # get the position of the rollout player in state to change the bid and set base_policy_player for simulate_episode
            base_policy_player_pos = -1
            for i in range(len(state_rollout_template.players_deal_order)):
                plr = state_rollout_template.players_deal_order[i]
                if plr.number == self.number:
                    base_policy_player_pos = i
            # simulate n times and store score
            # bid_scores = []
            bid_scores = Parallel(n_jobs=8)(delayed(self.sample_rollout_simulation)(state_rollout_template, base_policy_player_pos, bid) for i in range(0, 128))
            # for i in range(0, 128, 1):
            #     # create copy of the template rollout state
            #     state_rollout = State(state_rollout_template.players_deal_order, state_rollout_template.round_nr, state_rollout_template.trick, state_rollout_template.deck, state_rollout_template.bids, state_rollout_template.players_bid_order, state_rollout_template.players_play_order)
            #     # get base policy player from copied state
            #     base_policy_player = state_rollout.players_deal_order[base_policy_player_pos]
            #     base_policy_player.current_bid = bid
            #     # Simulate
            #     bid_scores.append(Simulation.simulate_episode(state_rollout, base_policy_player))
            bid_avg_score_dict[bid] = statistics.mean(bid_scores)
            #bid_stdev_score_dict[bid] = statistics.stdev(bid_scores)
            #bid_median_score_dict[bid] = statistics.median(bid_scores)
        max_avg_bid = max(bid_avg_score_dict, key=bid_avg_score_dict.get)
        return max_avg_bid

    @staticmethod
    def sample_rollout_simulation(state_rollout_template, base_policy_player_pos, bid):
        # create copy of the template rollout state
        state_rollout = State(state_rollout_template.players_deal_order, state_rollout_template.round_nr,
                              state_rollout_template.trick, state_rollout_template.deck,
                              state_rollout_template.bids, state_rollout_template.players_bid_order,
                              state_rollout_template.players_play_order)
        # get base policy player from copied state
        base_policy_player = state_rollout.players_deal_order[base_policy_player_pos]
        base_policy_player.current_bid = bid
        # Simulate
        result = Simulation.simulate_episode(state_rollout, base_policy_player)
        return result

    @staticmethod
    def generate_template_rollout_state(state):
        # get all rollout / human player positions in deal, bid and play lists
        human_players_positions = {}
        rollout_players_positions = {}
        for i in range(0, len(state.players_deal_order)):
            plr = state.players_deal_order[i]
            if isinstance(plr, PlayerHuman):
                human_players_positions[plr] = [i]
                human_players_positions[plr].append(PlayerComputerRollout.get_position_in_list(plr, state.players_bid_order))
                human_players_positions[plr].append(PlayerComputerRollout.get_position_in_list(plr, state.players_play_order))
            if isinstance(plr, PlayerComputerRollout):
                rollout_players_positions[plr] = [i]
                rollout_players_positions[plr].append(PlayerComputerRollout.get_position_in_list(plr, state.players_bid_order))
                rollout_players_positions[plr].append(PlayerComputerRollout.get_position_in_list(plr, state.players_play_order))
        # copy original state
        state_rollout = State(state.players_deal_order, state.round_nr, state.trick, state.deck, state.bids, state.players_bid_order, state.players_play_order)
        # substitute all human players with a myopic policy
        for plr in human_players_positions:
            human_substitute = PlayerComputerRollout.substitute_player(plr, PlayerComputerMyopic(plr.number, 'computer', 'myopic_human'))
            del state_rollout.players_deal_order[human_players_positions[plr][0]]
            state_rollout.players_deal_order.insert(human_players_positions[plr][0], human_substitute)
            del state_rollout.players_bid_order[human_players_positions[plr][1]]
            state_rollout.players_bid_order.insert(human_players_positions[plr][1], human_substitute)
            del state_rollout.players_play_order[human_players_positions[plr][2]]
            state_rollout.players_play_order.insert(human_players_positions[plr][2], human_substitute)

        base_policy_player = None
        # substitute rollout player with a myopic policy
        for plr in rollout_players_positions:
            base_policy_player = PlayerComputerRollout.substitute_player(plr, PlayerComputerMyopic(plr.number, 'computer', 'myopic_rollout'))
            # delete rollout player and insert base policy player
            del state_rollout.players_deal_order[rollout_players_positions[plr][0]]
            state_rollout.players_deal_order.insert(rollout_players_positions[plr][0], base_policy_player)
            del state_rollout.players_bid_order[rollout_players_positions[plr][1]]
            state_rollout.players_bid_order.insert(rollout_players_positions[plr][1], base_policy_player)
            del state_rollout.players_play_order[rollout_players_positions[plr][2]]
            state_rollout.players_play_order.insert(rollout_players_positions[plr][2], base_policy_player)
        return state_rollout

    @staticmethod
    def substitute_player(player, substitute):
        substitute.current_bid = player.current_bid
        substitute.current_hand = list(player.current_hand)
        substitute.played_cards = deque(player.played_cards)
        return substitute

    @staticmethod
    def get_position_in_list(player, player_list):
        for i in range(len(player_list)):
            p = player_list[i]
            if p == player:
                return i
