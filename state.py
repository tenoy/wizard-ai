

class State:

    def __init__(self, players, round_nr, trick, deck, bids):
        self.players = players
        self.round_nr = round_nr
        self.number_of_rounds = int(60 / len(players))
        self.trick = trick
        self.deck = deck
        self.bids = bids
