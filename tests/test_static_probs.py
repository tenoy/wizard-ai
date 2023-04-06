import random
import unittest

from card import Card
from deck import Deck
from enum_rank import Rank
from enum_suit import Suit
from trick import Trick


class TestStaticProb(unittest.TestCase):
    def generate_test_data(self):
        # Test dict. Contains the trick at idx=0, the trump suit at idx=1, leading_suit at idx=2 and the expected winning card at idx=3
        test_data = dict()

        test_data[0] = \
            (
            Trick(trump_suit=Suit.HEARTS, trump_card=Card(Suit.HEARTS, Rank.ACE), cards=[]),
            [Card(Suit.HEARTS, Rank.QUEEN)],  # represents current hand
            4, # number of players
            Card(Suit.HEARTS, Rank.QUEEN) # card to determine win prob
            )
        test_data[1] = \
            (
            Trick(trump_suit=Suit.HEARTS, trump_card=Card(Suit.HEARTS, Rank.ACE), cards=[]),
            [Card(Suit.JOKER, Rank.WIZARD, 1)],  # represents current hand
            4,  # number of players
            Card(Suit.JOKER, Rank.WIZARD, 1)  # card to determine win prob
            )

        return test_data

    def test_prob(self):
        test_data = self.generate_test_data()
        value = test_data[1]

        deck = Deck(False)
        deck.deck.remove(value[0].trump_card)
        deck.deck.remove(value[3])
        for i in range(0, len(value[1])):
            if value[1][i] != value[3]:
                deck.deck.remove(value[1][i])

        win_count = 0
        number_of_tricks = 100000
        # initialize dict with win count per position
        pos_win_count_dict = {}
        for i in range(0, value[2]):
            pos_win_count_dict[i] = 0

        for i in range(0, number_of_tricks):
            random_pos = random.randint(0, value[2]-1)
            value[0].cards = []
            for j in range(0, value[2]):
                if j == random_pos:
                    value[0].cards.append(value[3])
                else:
                    rand_idx = random.randint(0, len(deck.deck)-1)
                    random_card = deck.deck[rand_idx]
                    value[0].cards.append(random_card)
            highest_card = value[0].get_highest_trick_card_index()
            if highest_card == value[3]:
                win_count = win_count + 1
                pos_win_count_dict[random_pos] = pos_win_count_dict[random_pos] + 1

        print(f'Win count for {value[3]}: {win_count} of {number_of_tricks} tricks simulated -> prob: {win_count/number_of_tricks}')
        players = []
        for i in range(0, value[2]):
            players.append(i)
        print(f'Static win prob: {value[3].calc_static_win_prob(value[1], value[0].trump_card, players)}')
        print('test')
        # myopic_player = PlayerComputerMyopic(1, 'computer', "heuristic")
        # test_data = self.generate_test_data()
        # for i, value in test_data.items():
        #     print(str(value[0]) + ', max_prob_cards=' + str(value[1]) + ', expected: ' + str(value[2]))
        #     self.assertEqual(value[2], myopic_player.get_min_max_card(value[1], value[0]), "Failed test: " + str(i) + ". Should be: " + str(value[2]))