from __future__ import annotations
import itertools
import math
import statistics
from collections import deque
from joblib import Parallel, delayed
from player_human import PlayerHuman
from policies.player_computer_dynamic_weighted_random import PlayerComputerDynamicWeightedRandom
from policies.player_computer_myopic2 import PlayerComputerMyopic2
from policies.player_computer_random import PlayerComputerRandom
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from simulation import Simulation
from policies.player_computer_myopic import PlayerComputerMyopic

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from state import State
    from player import Player


class PlayerComputerRollout(PlayerComputerMyopic):

    def calculate_bid(self, state: State) -> int:
        # the original state must be copied and manipulated so that no rollout / human player are in the rollout state
        state_rollout_template = PlayerComputerRollout.generate_template_rollout_state(self, state, 'bid')

        # get the position of the rollout player in state to change the bid and set base_policy_player for simulate_episode
        base_policy_player_pos = -1
        for i in range(len(state.players_deal_order)):
            plr = state.players_deal_order[i]
            if plr.number == self.number:
                base_policy_player_pos = i

        decisions = []
        for i in range(0, state.round_nr+1):
            decisions.append(i)

        bid_avg_score_dict = self.calculate_rollout_values_izs(state=state_rollout_template, decisions=decisions, decision_type='bid', base_policy_player_pos=base_policy_player_pos, n_0=8, n_max=128, alpha=0.2, delta=9.0, batch_size=8)
        max_avg_bid = max(bid_avg_score_dict, key=bid_avg_score_dict.get)
        return max_avg_bid

    # rollout for playing decisions - computationally expensive and rollout for bid and playing decisions performed worse than bid rollout
    # def select_card(self, state, legal_cards, played_cards=None):
    #     # nothing to calculate if only 1 viable decision option is available
    #     if len(legal_cards) == 1:
    #         return legal_cards[0]
    #     # the original state must be copied and manipulated so that no rollout / human player are in the rollout state
    #     state_rollout_template = PlayerComputerRollout.generate_template_rollout_state(state, 'play')
    #     # get the position of the rollout player in state to change the selected card and set base_policy_player for simulate_episode
    #     base_policy_player_pos = -1
    #     for i in range(len(state.players_deal_order)):
    #         plr = state.players_deal_order[i]
    #         if plr.number == self.number:
    #             base_policy_player_pos = i
    #
    #     decisions = []
    #     for i in range(0, len(legal_cards)):
    #         decisions.append(i)
    #
    #     card_idx_avg_score_dict = self.calculate_rollout_values_izs(state=state_rollout_template, decisions=decisions, decision_type='play', base_policy_player_pos=base_policy_player_pos, n_0=8, n_max=128, alpha=0.2, delta=9.0, batch_size=8)
    #     max_avg_card_idx = max(card_idx_avg_score_dict, key=card_idx_avg_score_dict.get)
    #     return legal_cards[max_avg_card_idx]

    # Fully sequential procedure for indifference-zone selection (izs) (Kim & Nelson (2001))
    def calculate_rollout_values_izs(self, state: State, decisions: list[int], decision_type: Literal["bid", "play"], base_policy_player_pos: int, n_0: int, n_max: int, alpha: float, delta: float, batch_size: int) -> dict[int, float]:
        decision_values_dict = {}
        decisions_considered = []
        # initialization of izs
        for decision in range(0, len(decisions)):
            decisions_considered.append(decision)
            for i in range(0, n_0):
                res = self.sample_rollout_simulation(state, base_policy_player_pos, decision, decision_type)
                if decision in decision_values_dict:
                    decision_values_dict[decision].append(res)
                else:
                    decision_values_dict[decision] = list()
                    decision_values_dict[decision].append(res)

        # screening phase of izs
        i = n_0
        run_decision_mean_values_dict = {}
        run_decision_sigma_values_dict = {}
        run_decision_w_values_dict = {}
        decision_mean_scores_final_dict = {}
        with Parallel(n_jobs=batch_size) as parallel:
            while not(i > n_max or len(decisions_considered) < 2):
                i = i + batch_size
                decision_mean_scores_dict = {}
                for decision in decisions_considered:
                    # res = self.sample_rollout_simulation(state, base_policy_player_pos, bid)
                    # decision_values_dict[bid].append(res)
                    decision_values_dict[decision].extend(parallel(delayed(self.sample_rollout_simulation)(state, base_policy_player_pos, decision, decision_type) for j in range(0, batch_size)))
                    decision_mean_scores_dict[decision] = statistics.mean(decision_values_dict[decision])
                    decision_mean_scores_final_dict[decision] = statistics.mean(decision_values_dict[decision])

                run_decision_mean_values_dict[i] = decision_mean_scores_dict
                # update of h_2
                h_2 = (math.pow(((2*alpha) / (len(decisions_considered)-1)), (-2/(i-1))) - 1) * (i-1)
                # update sigma^2
                decision_j_decision_k_sigma_dict = {}
                decision_j_decision_k_w_dict = {}
                for j, k in itertools.permutations(decisions_considered, 2):
                    sum = 0
                    for r in range(0, i):
                        diff1 = decision_values_dict[j][r] - decision_values_dict[k][r]
                        diff2 = decision_mean_scores_final_dict[j] - decision_mean_scores_final_dict[k]
                        sum = sum + (diff1 - diff2)**2

                    sigma_2 = (1 / (i - 1)) * sum
                    decision_j_decision_k_sigma_dict[(j, k)] = sigma_2
                    # test = (delta/(2*i))*(((h_2*sigma_2)/delta**2)-i)
                    wjk = max(0, (delta/(2*i))*(((h_2*sigma_2)/delta**2)-i))
                    decision_j_decision_k_w_dict[(j, k)] = wjk

                # remove dominated bids
                run_decision_sigma_values_dict[i] = decision_j_decision_k_w_dict
                run_decision_w_values_dict[i] = decision_j_decision_k_w_dict
                decisions_to_keep = []
                for j in decisions_considered:
                    dominated = 0
                    for k in decisions_considered:
                        if j != k:
                            if decision_mean_scores_final_dict[j] < decision_mean_scores_final_dict[k] - decision_j_decision_k_w_dict[(j, k)]:
                                dominated = 1
                                break

                    if dominated == 0:
                        decisions_to_keep.append(j)

                decisions_considered = decisions_to_keep

        return decision_mean_scores_final_dict

    @staticmethod
    def sample_rollout_simulation(state_rollout_template: State, base_policy_player_pos: int, decision: int, decision_type: Literal["bid", "play"]) -> tuple[int, str] | dict[str, int]:
        # create copy of the template rollout state
        # state_rollout = State(players_deal_order=state_rollout_template.players_deal_order, round_nr=state_rollout_template.round_nr,
        #                       trick=state_rollout_template.trick, deck=state_rollout_template.deck,
        #                       bids=state_rollout_template.bids, players_play_order=state_rollout_template.players_play_order,
        #                       played_cards=state_rollout_template.played_cards)

        state_rollout = state_rollout_template.copy_state()

        # get base policy player from copied state
        base_policy_player = state_rollout.players_deal_order[base_policy_player_pos]
        if decision_type == 'bid':
            base_policy_player.current_bid = decision
        else:
            base_policy_player.current_card_idx = decision
        # Simulate
        result = Simulation.simulate_episode(state_rollout, base_policy_player)
        return result

    def generate_template_rollout_state(self, state: State, decision_type: Literal["bid", "play"]) -> State:
        # get all rollout / human player positions in deal, bid and play lists
        human_players_positions = {}
        rollout_players_positions = {}
        policy_name = 'rollout_' + decision_type
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

        for i in range(0, len(state.trick.played_by)):
            plr = state.trick.played_by[i]
            if isinstance(plr, PlayerHuman):
                human_players_positions[plr].append(i)
            if isinstance(plr, PlayerComputerRollout):
                rollout_players_positions[plr].append(i)

        # copy original state
        # state_rollout = State(players_deal_order=state.players_deal_order, round_nr=state.round_nr, trick=state.trick,
        #                       deck=state.deck, bids=state.bids, players_play_order=state.players_play_order, played_cards=state.played_cards)

        state_rollout = state.copy_state()

        # substitute human players and rollout players
        PlayerComputerRollout.substitute_player(self, state_rollout, human_players_positions, 'human_heuristic')
        PlayerComputerRollout.substitute_player(self, state_rollout, rollout_players_positions, policy_name)

        return state_rollout

    @staticmethod
    def copy_player(player: Player, substitute: Player) -> Player:
        substitute.current_bid = player.current_bid
        substitute.current_hand = list(player.current_hand)
        substitute.played_cards = deque(player.played_cards)
        return substitute

    @staticmethod
    def get_position_in_list(player: Player, player_list: deque[Player]) -> int:
        for i in range(len(player_list)):
            p = player_list[i]
            if p == player:
                return i

    def substitute_player(self, state_rollout: State, player_positions: dict[Player, list[int]], policy_name: str) -> None:
        base_policy = 'heuristic'
        policy_list = self.policy.split('-')
        if len(policy_list) > 1:
            base_policy = policy_list[1]
        full_policy_name = policy_name + '_' + base_policy
        for plr in player_positions:
            if base_policy == 'random':
                base_policy_player = PlayerComputerRollout.copy_player(plr, PlayerComputerRandom(plr.number, 'computer', full_policy_name))
            elif base_policy == 'weighted_random':
                base_policy_player = PlayerComputerRollout.copy_player(plr, PlayerComputerWeightedRandom(plr.number, 'computer', full_policy_name))
            elif base_policy == 'dynamic_weighted_random':
                base_policy_player = PlayerComputerRollout.copy_player(plr, PlayerComputerDynamicWeightedRandom(plr.number, 'computer', full_policy_name))
            elif base_policy == 'heuristic2':
                base_policy_player = PlayerComputerRollout.copy_player(plr, PlayerComputerMyopic2(plr.number, 'computer', full_policy_name))
            else:
                base_policy_player = PlayerComputerRollout.copy_player(plr, PlayerComputerMyopic(plr.number, 'computer', full_policy_name))
            # delete player and insert base policy player
            del state_rollout.players_deal_order[player_positions[plr][0]]
            state_rollout.players_deal_order.insert(player_positions[plr][0], base_policy_player)
            del state_rollout.players_bid_order[player_positions[plr][1]]
            state_rollout.players_bid_order.insert(player_positions[plr][1], base_policy_player)
            del state_rollout.players_play_order[player_positions[plr][2]]
            state_rollout.players_play_order.insert(player_positions[plr][2], base_policy_player)
            if len(player_positions[plr]) == 4:
                del state_rollout.trick.played_by[player_positions[plr][3]]
                state_rollout.trick.played_by.insert(player_positions[plr][3], base_policy_player)
