from player import Player


class PlayerHuman(Player):

    def is_input_valid(self, input_value):
        try:
            int(input_value)
            is_valid = True
        except ValueError:
            is_valid = False
        return is_valid

    def make_bid(self, round_nr, previous_bids, players, trump_suit):
        print('Trump suit: ' + str(trump_suit))
        print('Current hand:')
        print(*self.current_hand, sep=', ')
        print('Previous bids:', end=' ')
        print(*previous_bids)
        human_input = input('Enter your bid: ')
        while not self.is_input_valid(human_input):
            human_input = input('Invalid input, enter again: ')
        int_human_input = int(human_input)
        if not self.is_valid_bid(int_human_input, round_nr, previous_bids, players):
            print('Invalid bid, the sum of bids is not allowed to equal the round number')
            return self.make_bid(round_nr, previous_bids, players, trump_suit)
        else:
            return int_human_input

    def play(self, trick, leading_suit, trump_suit):
        print('Trump suit: ' + str(trump_suit))
        print('Cards in trick:', end=' ')
        print(*trick, sep=', ')
        print('Current hand:')
        for k in range(0, len(self.current_hand)):
            print('(' + str(k + 1) + ') ' + str(self.current_hand[k]) + ' ', end=' ')
        print('')
        idx = input('Select card: ')
        # todo: check selected card
        idx = int(idx) - 1
        selected_card = self.current_hand[idx]
        self.played_card = selected_card
        self.current_hand.remove(selected_card)
        return selected_card
