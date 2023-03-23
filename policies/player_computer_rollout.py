import itertools
import math
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

        # get the position of the rollout player in state to change the bid and set base_policy_player for simulate_episode
        base_policy_player_pos = -1
        for i in range(len(state.players_deal_order)):
            plr = state.players_deal_order[i]
            if plr.number == self.number:
                base_policy_player_pos = i

        # with Parallel(n_jobs=8) as parallel:
        # bid_avg_score_dict = {}
            #bid_stdev_score_dict = {}
            #bid_median_score_dict = {}
        # for bid in range(0, state.round_nr+1):
            # get the position of the rollout player in state to change the bid and set base_policy_player for simulate_episode
            # base_policy_player_pos = -1
            # for i in range(len(state_rollout_template.players_deal_order)):
            #     plr = state_rollout_template.players_deal_order[i]
            #     if plr.number == self.number:
            #         base_policy_player_pos = i
            # simulate n times and store score
            # bid_scores = []
            # bid_scores = parallel(delayed(self.sample_rollout_simulation)(state_rollout_template, base_policy_player_pos, bid) for i in range(0, 128))
            # bid_scores = Parallel(n_jobs=8)(delayed(self.sample_rollout_simulation)(state_rollout_template, base_policy_player_pos, bid) for i in range(0, 8))
            # for i in range(0, 128, 1):
            #     # create copy of the template rollout state
            #     state_rollout = State(state_rollout_template.players_deal_order, state_rollout_template.round_nr, state_rollout_template.trick, state_rollout_template.deck, state_rollout_template.bids, state_rollout_template.players_bid_order, state_rollout_template.players_play_order)
            #     # get base policy player from copied state
            #     base_policy_player = state_rollout.players_deal_order[base_policy_player_pos]
            #     base_policy_player.current_bid = bid
            #     # Simulate
            #     bid_scores.append(Simulation.simulate_episode(state_rollout, base_policy_player))
            # bid_avg_score_dict[bid] = statistics.mean(bid_scores)
            #bid_stdev_score_dict[bid] = statistics.stdev(bid_scores)
            #bid_median_score_dict[bid] = statistics.median(bid_scores)
        bid_avg_score_dict = self.calculate_bid_seq_izs(state=state_rollout_template, base_policy_player_pos=base_policy_player_pos, n_0=8, n_max=128, alpha=0.2, delta=9.0, batch_size=8)
        max_avg_bid = max(bid_avg_score_dict, key=bid_avg_score_dict.get)
        return max_avg_bid

    # Fully sequential procedure for indifference-zone selection (izs) (Kim & Nelson (2001))
    def calculate_bid_seq_izs(self, state, base_policy_player_pos, n_0, n_max, alpha, delta, batch_size):
        bid_values_dict = {}
        bids_considered = []
        # initialization of izs
        for bid in range(0, state.round_nr + 1):
            bids_considered.append(bid)
            for i in range(0, n_0):
                res = self.sample_rollout_simulation(state, base_policy_player_pos, bid)
                if bid in bid_values_dict:
                    bid_values_dict[bid].append(res)
                else:
                    bid_values_dict[bid] = list()
                    bid_values_dict[bid].append(res)

        # screening phase of izs
        i = n_0
        run_bid_mean_values_dict = {}
        run_bid_sigma_values_dict = {}
        run_bid_w_values_dict = {}
        bid_mean_scores_final_dict = {}
        with Parallel(n_jobs=batch_size) as parallel:
            while not(i > n_max or len(bids_considered) < 2):
                i = i + batch_size
                bid_mean_scores_dict = {}
                for bid in bids_considered:
                    # res = self.sample_rollout_simulation(state, base_policy_player_pos, bid)
                    # bid_values_dict[bid].append(res)
                    bid_values_dict[bid].extend(parallel(delayed(self.sample_rollout_simulation)(state, base_policy_player_pos, bid) for j in range(0, batch_size)))
                    bid_mean_scores_dict[bid] = statistics.mean(bid_values_dict[bid])
                    bid_mean_scores_final_dict[bid] = statistics.mean(bid_values_dict[bid])

                run_bid_mean_values_dict[i] = bid_mean_scores_dict
                # update of h_2
                h_2 = (math.pow(((2*alpha) / (len(bids_considered)-1)), (-2/(i-1))) - 1) * (i-1)
                # update sigma^2
                bidj_bidk_sigma_dict = {}
                bidj_bidk_w_dict = {}
                for j, k in itertools.permutations(bids_considered, 2):
                    sum = 0
                    for r in range(0, i):
                        diff1 = bid_values_dict[j][r] - bid_values_dict[k][r]
                        diff2 = bid_mean_scores_final_dict[j] - bid_mean_scores_final_dict[k]
                        sum = sum + (diff1 - diff2)**2

                    sigma_2 = (1 / (i - 1)) * sum
                    bidj_bidk_sigma_dict[(j, k)] = sigma_2
                    # test = (delta/(2*i))*(((h_2*sigma_2)/delta**2)-i)
                    wjk = max(0, (delta/(2*i))*(((h_2*sigma_2)/delta**2)-i))
                    bidj_bidk_w_dict[(j, k)] = wjk

                # remove dominated bids
                run_bid_sigma_values_dict[i] = bidj_bidk_w_dict
                run_bid_w_values_dict[i] = bidj_bidk_w_dict
                bids_to_keep = []
                for j in bids_considered:
                    dominated = 0
                    for k in bids_considered:
                        if j != k:
                            if bid_mean_scores_final_dict[j] < bid_mean_scores_final_dict[k] - bidj_bidk_w_dict[(j, k)]:
                                dominated = 1
                                break

                    if dominated == 0:
                        bids_to_keep.append(j)

                bids_considered = bids_to_keep

        return bid_mean_scores_final_dict

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
