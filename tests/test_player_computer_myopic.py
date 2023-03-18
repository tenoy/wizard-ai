import unittest

from card import Card
from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_myopic import PlayerComputerMyopic
from trick import Trick


class TestMyopicFunctions(unittest.TestCase):

    def generate_test_data(self):
        # Test dict. Contains the trick at idx=0, the max_prob_cards at idx=1, the expected min_max_card at idx=2
        test_data = dict()

        test_data[0] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=None,
                  cards=[Card(Suit.JOKER, Rank.JESTER, 1), Card(Suit.JOKER, Rank.JESTER, 2)]),
            [Card(Suit.HEARTS, Rank.TWO), Card(Suit.CLUBS, Rank.ACE)],
            Card(Suit.CLUBS, Rank.ACE)
            )

        test_data[1] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=None,
                  cards=[Card(Suit.JOKER, Rank.JESTER, 1), Card(Suit.JOKER, Rank.JESTER, 2)]),
            [Card(Suit.HEARTS, Rank.TWO), Card(Suit.CLUBS, Rank.ACE),  Card(Suit.SPADES, Rank.KING)],
            Card(Suit.SPADES, Rank.KING)
            )

        test_data[2] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=Suit.CLUBS,
                  cards=[Card(Suit.CLUBS, Rank.TWO), Card(Suit.CLUBS, Rank.THREE)]),
            [Card(Suit.JOKER, Rank.WIZARD, 1), Card(Suit.CLUBS, Rank.ACE)],
            Card(Suit.CLUBS, Rank.ACE)
            )

        test_data[3] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=Suit.CLUBS,
                  cards=[Card(Suit.CLUBS, Rank.TWO), Card(Suit.CLUBS, Rank.THREE)]),
            [Card(Suit.CLUBS, Rank.ACE), Card(Suit.JOKER, Rank.WIZARD, 1)],
            Card(Suit.CLUBS, Rank.ACE)
            )

        test_data[4] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=Suit.CLUBS,
                  cards=[Card(Suit.CLUBS, Rank.TWO), Card(Suit.CLUBS, Rank.THREE)]),
            [Card(Suit.JOKER, Rank.WIZARD, 1), Card(Suit.HEARTS, Rank.ACE)],
            Card(Suit.HEARTS, Rank.ACE)
            )

        test_data[5] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=Suit.CLUBS,
                  cards=[Card(Suit.CLUBS, Rank.TWO), Card(Suit.CLUBS, Rank.THREE)]),
            [Card(Suit.HEARTS, Rank.ACE), Card(Suit.JOKER, Rank.WIZARD, 1)],
            Card(Suit.HEARTS, Rank.ACE)
            )

        test_data[6] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=None,
                  cards=[Card(Suit.JOKER, Rank.JESTER, 1), Card(Suit.JOKER, Rank.JESTER, 2)]),
            [Card(Suit.HEARTS, Rank.ACE), Card(Suit.JOKER, Rank.WIZARD, 1), Card(Suit.SPADES, Rank.ACE)],
            Card(Suit.SPADES, Rank.ACE)
            )

        test_data[7] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=None,
                  cards=[Card(Suit.JOKER, Rank.JESTER, 1), Card(Suit.JOKER, Rank.JESTER, 2)]),
            [Card(Suit.SPADES, Rank.ACE), Card(Suit.JOKER, Rank.WIZARD, 1), Card(Suit.HEARTS, Rank.ACE)],
            Card(Suit.SPADES, Rank.ACE)
            )

        test_data[8] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=None,
                  cards=[Card(Suit.JOKER, Rank.JESTER, 1), Card(Suit.JOKER, Rank.JESTER, 2)]),
            [Card(Suit.SPADES, Rank.ACE), Card(Suit.JOKER, Rank.WIZARD, 1), Card(Suit.HEARTS, Rank.ACE), Card(Suit.DIAMONDS, Rank.TWO)],
            Card(Suit.DIAMONDS, Rank.TWO)
            )

        test_data[9] = \
            (
            Trick(trump_suit=Suit.HEARTS, leading_suit=Suit.CLUBS,
                  cards=[Card(Suit.CLUBS, Rank.TWO), Card(Suit.CLUBS, Rank.THREE)]),
            [Card(Suit.DIAMONDS, Rank.ACE), Card(Suit.JOKER, Rank.JESTER, 1)],
            Card(Suit.DIAMONDS, Rank.ACE)
            )

        return test_data

    def test_get_min_max_card(self):
        myopic_player = PlayerComputerMyopic(1, 'computer', "heuristic")
        test_data = self.generate_test_data()
        for i, value in test_data.items():
            print(str(value[0]) + ', max_prob_cards=' + str(value[1]) + ', expected: ' + str(value[2]))
            self.assertEqual(value[2], myopic_player.get_min_max_card(value[1], value[0]), "Failed test: " + str(i) + ". Should be: " + str(value[2]))