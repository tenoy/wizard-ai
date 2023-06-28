from __future__ import annotations
import queue
import sys
import time
from enum_suit import Suit
from player import Player
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from state import State
    from card import Card


class PlayerHuman(Player):

    input_q = None
    output_q = None

    def __init__(self, number: int, player_type: Literal["human"], player_name: str='', input_q: queue.Queue=None, output_q: queue.Queue=None) -> None:
        super(PlayerHuman, self).__init__(number, player_type)
        self.name = player_name
        PlayerHuman.input_q = input_q
        PlayerHuman.output_q = output_q

    def __str__(self) -> str:
        return 'Player_' + str(self.number) + ' ' + self.name

    def __repr__(self) -> str:
        return 'Player_' + str(self.number) + ' ' + self.name

    @staticmethod
    def is_input_valid(input_value: int) -> bool:
        if input_value is None:
            return False
        try:
            input_int = int(input_value)
            if input_int < 0:
                is_valid = False
            else:
                is_valid = True
        except ValueError:
            is_valid = False
        return is_valid

    def make_bid(self, state: State) -> int:
        bid = -1
        print('Round: ' + str(state.round_nr))
        print('Current Scores: ', end=' ')
        print(*['(' + str(player) + ': ' + str(player.current_score) + ')' for player in state.players_deal_order])
        print('Trump card: ' + str(state.trick.trump_card))
        print('Trump suit: ' + str(state.trick.trump_suit))
        print('Current hand:')
        print(*self.current_hand, sep=', ')
        print('Previous bids:', end=' ')
        print(*state.bids.items())
        is_valid_input = False
        while not is_valid_input:
            # print(f'human:  {PlayerHuman.input_q.queue}')
            # print('human: loop')
            # print('human: putting ENTER_BID')
            PlayerHuman.input_q.put('ENTER_BID')
            # print(f'human:  {PlayerHuman.input_q.queue}')
            # print('human: waiting for all tasks done')
            PlayerHuman.input_q.join()
            # print('human: input q joined')
            is_bid_input_received = False
            while not is_bid_input_received:
                try:
                    # time.sleep(0.05)
                    # print(f'human bid: call get bid from output q: {PlayerHuman.output_q.queue}')
                    msg = PlayerHuman.output_q.get(block=True, timeout=0.05)
                    if msg[0] == 'INPUT_BID':
                        human_input = msg[1]
                        # print(f'human: input: {msg[1]}')
                        is_bid_input_received = True
                        if self.is_input_valid(human_input):
                            int_human_input = int(human_input)
                            if self.is_valid_bid(state, int_human_input):
                                bid = int_human_input
                                is_valid_input = True
                                # print(f'human: valid input')
                                # print(f'human: task done')
                                # print(f'human:  {PlayerHuman.output_q.queue}')
                                PlayerHuman.output_q.task_done()
                            else:
                                print('Invalid bid. The sum of bids is not allowed to equal the round number')
                                is_valid_input = False
                                # print(f'human: task done')
                                # print(f'human:  {PlayerHuman.output_q.queue}')
                                PlayerHuman.output_q.task_done()
                                PlayerHuman.input_q.put('INVALID_BID')
                                PlayerHuman.input_q.join()
                        else:
                            print('Invalid input. Input must be a positive number.')
                            is_valid_input = False
                            # print(f'human: task done')
                            # print(f'human:  {PlayerHuman.output_q.queue}')
                            PlayerHuman.output_q.task_done()
                            PlayerHuman.input_q.put('INVALID_INPUT')
                            PlayerHuman.input_q.join()
                    elif msg == 'GAME_RESTART':
                        print('GAME_RESTART received! Restarting...')
                        is_valid_input = True
                        is_bid_input_received = True
                        PlayerHuman.output_q.task_done()
                        sys.exit()
                    else:
                        print(f'(Bid) Other msg code: {msg}')
                        PlayerHuman.output_q.task_done()
                except queue.Empty:
                    # print(f'human bid: empty q: {PlayerHuman.output_q.queue}')
                    time.sleep(0.01)
        # print('human: loop left')
        # print(f'return value: {bid}')
        return bid

    def play(self, state: State) -> Card:
        selected_card = None
        idx = -1
        print('Bids: ', end=' ')
        print(*state.bids.items())
        print('Trump card: ' + str(state.trick.trump_card))
        print('Trump suit: ' + str(state.trick.trump_suit))
        print('Cards in trick:', end=' ')
        print(*state.trick.cards, sep=', ')
        self.print_current_hand()

        is_valid_input = False
        while not is_valid_input:
            is_card_input_received = False
            while not is_card_input_received:
                try:
                    # print(f'human play: get card from output_q: {PlayerHuman.output_q.queue}')
                    msg = PlayerHuman.output_q.get(block=True, timeout=0.05)
                    if msg[0] == 'INPUT_CARD':
                        selected_card = msg[1]
                        is_card_input_received = True
                        if self.is_valid_card(selected_card, state.trick.leading_suit):
                            self.played_cards.appendleft(selected_card)
                            self.current_hand.remove(selected_card)
                            is_valid_input = True
                            PlayerHuman.output_q.task_done()
                        else:
                            print('Invalid Card. You have at least one card that fits the suit. You must either play a card with fitting suit or a joker.')
                            is_valid_input = False
                            PlayerHuman.output_q.task_done()
                            PlayerHuman.input_q.put('INVALID_CARD')
                            PlayerHuman.input_q.join()
                    elif msg == 'GAME_RESTART':
                        print('GAME_RESTART received! Restarting...')
                        is_valid_input = True
                        is_card_input_received = True
                        PlayerHuman.output_q.task_done()
                        sys.exit()
                    else:
                        print(f'(Play) Other msg code: {msg}')
                        PlayerHuman.output_q.task_done()
                except queue.Empty:
                    # print(f'human play: empty output_q: {PlayerHuman.output_q.queue}')
                    time.sleep(0.05)

        return selected_card

    def pick_suit(self, state: State) -> Suit:
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
            is_suit_input_received = False
            # print('human: putting SELECT_SUIT')
            PlayerHuman.input_q.put('SELECT_SUIT')
            # print(f'human:  {PlayerHuman.input_q.queue}')
            # print('human: waiting for all tasks done')
            PlayerHuman.input_q.join()
            while not is_suit_input_received:
                try:
                    msg = PlayerHuman.output_q.get(block=True, timeout=0.05)
                    if msg[0] == 'INPUT_SUIT':
                        selected_suit = msg[1]
                        is_suit_input_received = True
                        if selected_suit.name != "JOKER":
                            is_valid_input = True
                            # print(f'selected {selected_suit}')
                            PlayerHuman.output_q.task_done()
                        else:
                            is_valid_input = False
                            PlayerHuman.output_q.task_done()
                    else:
                        # print(f'(Select Suit) Other msg code: {msg}')
                        PlayerHuman.output_q.task_done()
                except queue.Empty:
                    # print(f'human suit: empty output_q: {PlayerHuman.output_q.queue}')
                    time.sleep(0.05)

        return selected_suit
