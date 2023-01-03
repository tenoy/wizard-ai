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
        pos_rollout_player = -1
        pos_humans = []
        for i in range(0, len(state.players)):
            if self == state.players[i]:
                pos_rollout_player = i
            if state.players[i].player_type == 'human':
                pos_humans.append(i)


        bid_avg_score_dict = {}
        #bid_stdev_score_dict = {}
        #bid_median_score_dict = {}
        for bid in range(0, state.round_nr):
            # simulate n times and store score
            bid_scores = []
            for i in range(0, 128, 1):
                # create copy of state
                state_rollout = State(state.players, state.round_nr, state.trick, state.deck, state.bids)
                # substitute every human player in copied state
                for j in pos_humans:
                    human_substitute = PlayerComputerRollout.substitute_player(state.players[j], PlayerComputerMyopic(self.number, 'computer', 'human_substitute_rollout'))
                    del state_rollout.players[j]
                    state_rollout.players.insert(j, human_substitute)
                # substitute rollout player
                base_policy_player = PlayerComputerRollout.substitute_player(self, PlayerComputerMyopic(self.number, 'computer', 'myopic_rollout'))
                # set bid to evaluate
                base_policy_player.current_bid = bid
                # delete rollout player and insert base policy player
                del state_rollout.players[pos_rollout_player]
                state_rollout.players.insert(pos_rollout_player, base_policy_player)
                # Simulate
                bid_scores.append(Simulation.simulate_episode(state_rollout, 0, base_policy_player))
            bid_avg_score_dict[bid] = statistics.mean(bid_scores)
            #bid_stdev_score_dict[bid] = statistics.stdev(bid_scores)
            #bid_median_score_dict[bid] = statistics.median(bid_scores)
        bid = max(bid_avg_score_dict, key=bid_avg_score_dict.get)
        return bid

    @staticmethod
    def substitute_player(player, substitute):
        substitute.current_bid = player.current_bid
        substitute.current_hand = list(player.current_hand)
        substitute.played_cards = deque(player.played_cards)
        return substitute
