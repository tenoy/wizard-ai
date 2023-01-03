from enum_suit import Suit
from player import Player


class PlayerHuman(Player):

    def is_input_valid(self, input_value):
        try:
            int(input_value)
            is_valid = True
        except ValueError:
            is_valid = False
        return is_valid

    def make_bid(self, state):
        bid = -1
        print('Round: ' + str(state.round_nr))
        print('Trump suit: ' + str(state.trick.trump_suit))
        print('Current hand:')
        print(*self.current_hand, sep=', ')
        print('Previous bids:', end=' ')
        print(*state.bids.items())
        is_valid_input = False
        while not is_valid_input:
            human_input = input('Enter your bid: ')
            if self.is_input_valid(human_input):
                int_human_input = int(human_input)
                if self.is_valid_bid(state, int_human_input):
                    bid = int_human_input
                    is_valid_input = True
                else:
                    print('Invalid bid. The sum of bids is not allowed to equal the round number')
                    is_valid_input = False
            else:
                print('Invalid input. Input must be a positive number.')
                is_valid_input = False

        return bid

    def play(self, trick, bids):
        selected_card = None
        idx = -1
        print('Bids: ', end=' ')
        print(*bids.items())
        print('Trump suit: ' + str(trick.trump_suit))
        print('Cards in trick:', end=' ')
        print(*trick.cards, sep=', ')
        self.print_current_hand()
        is_valid_input = False
        while not is_valid_input:
            human_input = input('Select card: ')
            if self.is_input_valid(human_input):
                int_human_input = int(human_input)
                if 0 < int_human_input <= len(self.current_hand):
                    idx = int_human_input - 1
                    selected_card = self.current_hand[idx]
                    if self.is_valid_card(selected_card, trick.leading_suit):
                        self.played_cards.appendleft(selected_card)
                        self.current_hand.remove(selected_card)
                        is_valid_input = True
                    else:
                        print('Invalid Card. You have at least one card that fits the suit. You must either play a card with fitting suit or a joker.')
                        is_valid_input = False
                else:
                    print('Invalid input. Input must be a number between 1 and ' + str(len(self.current_hand)) + '.')
                    is_valid_input = False
            else:
                is_valid_input = False
        return selected_card

    def pick_suit(self, state):
        selected_suit = None
        print('Round: ' + str(state.round_nr))
        print('You are the dealer and have drawn a WIZARD as the trump card. You may choose a suit.')
        self.print_current_hand()
        i = 1
        print('Suits')
        for suit in Suit:
            if suit != Suit.JOKER:
                print('(' + str(i) + ') ' + str(suit) + ' ', end=' ')
            i = i + 1
        print('')
        is_valid_input = False
        while not is_valid_input:
            human_input = input('Select suit: ')
            if self.is_input_valid(human_input):
                int_human_input = int(human_input)
                if 0 < int_human_input <= len(Suit)-1:
                    idx = int_human_input
                    selected_suit = Suit(idx)
                    is_valid_input = True
                else:
                    print('Invalid input. Input must be a number between 1 and ' + str(
                        len(Suit)-1) + '.')
                    is_valid_input = False
            else:
                print('Invalid input. Input must be a number.')
                is_valid_input = False

        return selected_suit
