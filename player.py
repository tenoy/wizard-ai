import random


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.current_hand = []
        self.score = 0
        self.current_bid = -1

    def make_bid(self, round_nr):
        return random.uniform(0, round_nr)

    def play(self):
        rnd_card = random.uniform(0, len(self.current_hand)-1)
        selected_card = self.current_hand[rnd_card]
        return selected_card






