import unittest

from card import Card
from enum_rank import Rank
from enum_suit import Suit
from trick import Trick


class TestTrickFunctions(unittest.TestCase):
    def generate_test_tricks(self):
        # Test dict. Contains the trick at idx=0, the trump suit at idx=1, leading_suit at idx=2 and the expected winning card at idx=3
        test_tricks = dict()

        test_tricks[0] = \
            (
            Trick(trump_suit=None,
                  cards=[]),
            None,
            None
            )

        test_tricks[1] = \
            (
            Trick(trump_suit=Suit.HEARTS,
                  cards=[Card(Suit.JOKER, Rank.WIZARD, 1), Card(Suit.JOKER, Rank.WIZARD, 2), Card(Suit.JOKER, Rank.WIZARD, 3)]),
            Card(Suit.JOKER, Rank.WIZARD, 1),
            None
            )

        test_tricks[2] = \
            (
            Trick(trump_suit=Suit.DIAMONDS,
                  cards=[Card(Suit.JOKER, Rank.JESTER, 1), Card(Suit.JOKER, Rank.JESTER, 2), Card(Suit.JOKER, Rank.JESTER, 3)]),
            Card(Suit.JOKER, Rank.JESTER, 1),
            None
            )

        test_tricks[3] = \
            (
            Trick(trump_suit=Suit.DIAMONDS,
                  cards=[Card(Suit.JOKER, Rank.JESTER, 1), Card(Suit.JOKER, Rank.WIZARD, 1), Card(Suit.HEARTS, Rank.TWO)]),
            Card(Suit.JOKER, Rank.WIZARD, 1),
            None
            )

        test_tricks[4] = \
            (
            Trick(trump_suit=Suit.CLUBS,
                  cards=[Card(Suit.SPADES, Rank.ACE), Card(Suit.CLUBS, Rank.TWO), Card(Suit.JOKER, Rank.JESTER, 1)]),
            Card(Suit.CLUBS, Rank.TWO),
            Suit.SPADES
            )

        test_tricks[5] = \
            (
            Trick(trump_suit=Suit.HEARTS,
                  cards=[Card(Suit.DIAMONDS, Rank.QUEEN), Card(Suit.CLUBS, Rank.TWO), Card(Suit.DIAMONDS, Rank.ACE)]),
            Card(Suit.DIAMONDS, Rank.ACE),
            Suit.DIAMONDS
            )

        test_tricks[6] = \
            (
                Trick(trump_suit=Suit.HEARTS,
                      cards=[Card(Suit.HEARTS, Rank.ACE), Card(Suit.JOKER, Rank.WIZARD),
                             Card(Suit.DIAMONDS, Rank.ACE)]),
                Card(Suit.JOKER, Rank.WIZARD),
                Suit.HEARTS
            )

        test_tricks[7] = \
            (
                Trick(trump_suit=Suit.DIAMONDS,
                      cards=[Card(Suit.JOKER, Rank.WIZARD), Card(Suit.DIAMONDS, Rank.TWO),
                             Card(Suit.SPADES, Rank.KING)]),
                Card(Suit.JOKER, Rank.WIZARD),
                None
            )

        return test_tricks

    def test_get_highest_card_in_trick(self):
        test_tricks = self.generate_test_tricks()
        for _, value in test_tricks.items():
            print(str(value[0].cards) + ', trump=' + str(value[1]) + ', win=' + str(value[1]))
            self.assertEqual(value[0].get_highest_trick_card(), value[1], "Should be: " + str(value[1]))

    def test_get_leading_suit(self):
        test_tricks = self.generate_test_tricks()
        for _, value in test_tricks.items():
            print(str(value[0].cards) + ', trump=' + str(value[1]) + ', suit=' + str(value[2]))
            self.assertEqual(value[0].get_leading_suit(), value[2], "Should be: " + str(value[2]))