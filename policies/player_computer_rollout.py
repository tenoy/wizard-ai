from simulation import Simulation
from card import Card
from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_myopic import PlayerComputerMyopic
from state import State


class PlayerComputerRollout(PlayerComputerMyopic):

    def calculate_bid(self, state):
        # todo: change player list so that rollout policy player becomes base policy player
        state_rollout = State(state.players, state.round_nr, state.trick, state.deck, state.bids)
        Simulation.simulate_episode(state_rollout, 1, True)
        print('stub')
