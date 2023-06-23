
class TreeNode:

    def __init__(self):
        self.parent_node = None
        self.child_nodes = list()
        # the state var must be extended to information sets (i.e. a set of states that the agent believes the game to be in)
        self.state = None
        self.decision = None
