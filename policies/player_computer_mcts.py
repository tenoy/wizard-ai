from __future__ import annotations
import math
from policies.player_computer_rollout import PlayerComputerRollout
from policies.utils.tree_node import TreeNode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import State
    from card import Card
    from trick import Trick
    from player import Player


# Implementation of the Monte Carlo Tree Search (MCTS) / Information Set MCTS algorithm
class PlayerComputerMCTS(PlayerComputerRollout):

    def select_card(self, state: State, legal_cards: list[Card], played_cards: list[Card]=None) -> Card:
        # start a root
        root = TreeNode()
        # add all possible decisions as child nodes to root
        for i in range(0, len(legal_cards)):
            node = TreeNode()
            node.parent_node = root
            root.child_nodes.append(node)

    def select_node(self, current_node: TreeNode):
        node_ucb_score_dict = {}
        for child_node in current_node.child_nodes:
            node_ucb_score_dict[child_node] = self.calculate_ucb1(current_node, child_node)
        node_ucb_score_dict_sorted = sorted(node_ucb_score_dict, key=node_ucb_score_dict.get, reverse=True)
        ties = []
        highest_node = node_ucb_score_dict_sorted[0]

    def expand_node(self, current_node: TreeNode):
        pass

    def rollout(self):
        # logic for rollout here, basically just call calculate_rollout_values_izs and return avg of that
        pass

    def backpropagate(self, current_node: TreeNode, config):
        val = current_node.get_lte().get_value()
        while current_node.get_parent_node() is not None:
            parent_node = current_node.get_parent_node()
            parent_node.get_lte().update(val, config)
            # parentNode.getLte().setValue(val)
            parent_node.get_lte().set_value_sums(val)
            current_node = parent_node

    def calculate_ucb1(self, parent_node: TreeNode, child_node: TreeNode):
        constant_c = 2
        parent_count = parent_node.get_lte().get_counter()
        child_count = child_node.get_lte().get_counter()
        avg_value = child_node.get_lte().get_value()
        if parent_count == 0 or child_count == 0:
            ucb = avg_value
        else:
            ucb = avg_value + constant_c * math.sqrt(math.log(parent_count) / child_count)
        return ucb