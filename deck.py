from card import Card
from enum_rank import Rank
from enum_suit import Suit


class Deck:

    def __init__(self, is_game_mode):
        self.deck = []
        # generate normal cards
        for i in range(1, 5):
            for j in range(2, 15, 1):
                c = Card(Suit(i), Rank(j), is_game_mode=is_game_mode)
                self.deck.append(c)
                # print(c)

        # generate jesters
        for i in range(1, 5):
            c = Card(Suit.JOKER, Rank.JESTER, i, is_game_mode=is_game_mode)
            self.deck.append(c)
            # print(c)

        # generate wizards
        for i in range(1, 5):
            c = Card(Suit.JOKER, Rank.WIZARD, i, is_game_mode=is_game_mode)
            self.deck.append(c)