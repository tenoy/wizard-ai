import unittest

from card import Card
from enum_rank import Rank
from enum_suit import Suit
from utils import get_highest_legal_card


class TestUtilFunctions(unittest.TestCase):

    def generate_test_legal_hands(self):
        test_legal_hands = dict()
        test_legal_hands[0] = ([], None, None, None)
        test_legal_hands[1] = ([Card(Suit.HEARTS, Rank.TWO, 0), Card(Suit.CLUBS, Rank.SEVEN, 0)],
                               Suit.HEARTS, None, Card(Suit.HEARTS, Rank.TWO, 0))
        test_legal_hands[2] = ([Card(Suit.HEARTS, Rank.TWO, 0), Card(Suit.DIAMONDS, Rank.NINE, 0)],
                               Suit.CLUBS, None, Card(Suit.DIAMONDS, Rank.NINE, 0))
        return test_legal_hands

    def test_get_highest_legal_card(self):
        test_legal = self.generate_test_legal_hands()
        for _, value in test_legal.items():
            print(str(value[0]) + ', trump=' + str(value[1]) + ', win=' + str(value[3]))
            self.assertEqual(get_highest_legal_card(value[0], value[1], value[2]), value[3], "Should be: " + str(value[3]))

    # prob_2_players = ((3 - n_jesters_played) / (59 - n_cards_played))
    # prob_3_players = ((3 - n_jesters_played) / (59 - n_cards_played)) * ((2 - n_jesters_played) / (58 - n_cards_played))
    # prob_4_players = ((3 - n_jesters_played) / (59 - n_cards_played)) * ((2 - n_jesters_played) / (58 - n_cards_played)) * ((1 - n_jesters_played) / (57 - n_cards_played))


if __name__ == '__main__':
    unittest.main()