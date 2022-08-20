class State():
    def __init__(self, players, round_nr, trick, deck, bids, trump_suit):
        self.players = players
        self.round_nr = round_nr
        self.trick = trick
        self.deck = deck
        self.bids = bids
        self.trump_suit = trump_suit
