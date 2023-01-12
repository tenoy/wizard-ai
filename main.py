import queue
import sys
import textwrap
import threading
import time
from collections import deque
from tkinter import Tk, ttk, Label

from PIL import ImageTk

from player_gui import PlayerGui
from simulation import Simulation
from card import Card
from enum_rank import Rank
from enum_suit import Suit
from player_human import PlayerHuman
from policies.player_computer_dynamic_weighted_random import PlayerComputerDynamicWeightedRandom
from policies.player_computer_myopic import PlayerComputerMyopic
from policies.player_computer_random import PlayerComputerRandom
from policies.player_computer_rollout import PlayerComputerRollout
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from state import State
from trick import Trick
import datetime


# def get_human_player(state):
#     human_plr = None
#     for plr in state.players:
#         if plr.player_type == 'human':
#             human_plr = plr
#     return human_plr
#
# global card_images_hand
# card_images_hand = []

# def update_hand():
#     print('###update hand###')
#     human_plr = get_human_player(s0)
#     hand_group = ttk.LabelFrame(mainframe, text=f'Current hand {human_player}')
#     hand_group.grid(padx=pad_x, pady=pad_y, row=2, column=0, columnspan=2)
#     #card_images_hand = []
#     for crd in human_plr.current_hand:
#         card_images_hand.append(ImageTk.PhotoImage(crd.card_image))
#     max_cards_per_row = 7
#     current_row = 0
#     current_col = 0
#     for i2 in range(len(human_plr.current_hand)):
#         if current_col >= max_cards_per_row:
#             current_row = current_row + 1
#             current_col = 0
#         card_labl = Label(hand_group, text='', image=card_images_hand[i2])  # get image of card
#         card_labl.grid(row=current_row, column=current_col)
#         current_col = current_col + 1


def process_simulation_event_queue(q):
    while True:
        # time.sleep(0.05)
        try:
            print(f'poll:  {q.queue}')
            msg = q.get(block=True)
            if msg == "UPDATE_HAND":
                gui.update_hand(s0)
                #update_hand()
                q.task_done()
            elif msg == "UPDATE_TRUMP":
                # print('update trump')
                gui.update_trump(s0)
                q.task_done()
            elif msg == "UPDATE_STATS":
                # print('update stats')
                gui.update_stats(s0)
                q.task_done()
            elif msg == "UPDATE_TRICK":
                # print('update trick')
                gui.update_trick(s0)
                q.task_done()
            elif msg == "UPDATE_ROUND":
                # print('update round')
                gui.update_round(s0)
                q.task_done()
            elif msg == "UPDATE_TRICK_WINNER":
                # print('update trick winner')
                gui.update_trick_winner(s0)
                q.task_done()
            elif msg == "ENTER_BID":
                print('poll: call enter bid gui')
                bid = gui.enter_bid()
                # bid = root.after(0, gui.enter_bid)
                print(f'poll: bid value: {bid}')
                print(f'poll: task done')
                print(f'poll:  {q.queue}')
                q.task_done()
                print('poll: putting INPUT_BID')
                q.put('INPUT_BID')
                print(f'poll:  {q.queue}')
                print('poll: waiting for all tasks done')
                q.join()
                print('poll: q joined')
                print('poll: putting bid')
                print(f'poll:  {q.queue}')
                q.put(bid)
                print(f'poll:  {q.queue}')
                # print(q.queue)
                # print('poll: waiting for all tasks done')
                # q.join()
                # print('poll: q joined')
                # q.task_done()
                # print(q.queue)
        except queue.Empty:
            print('poll: sleep')
            time.sleep(0.05)


# program mode is either 'game' (with human player) or 'simulation' (only computers)
global program_mode
program_mode = 'game'

if program_mode == 'game':
    is_game_mode = True
else:
    is_game_mode = False

deck = []
for i in range(1, 5):
    for j in range(2, 15, 1):
        c = Card(Suit(i), Rank(j), is_game_mode=is_game_mode)
        deck.append(c)
        #print(c)

for i in range(1, 5):
    c = Card(Suit.JOKER, Rank.JESTER, i, is_game_mode=is_game_mode)
    deck.append(c)
    #print(c)

for i in range(1, 5):
    c = Card(Suit.JOKER, Rank.WIZARD, i, is_game_mode=is_game_mode)
    deck.append(c)
    #print(c)


if program_mode == 'simulation':
    timestamp_start = datetime.datetime.now()

    for i in range(0, 1000):
        players_initial_order = deque()
        players_initial_order.append(PlayerComputerRandom(1, 'computer', "random"))
        players_initial_order.append(PlayerComputerWeightedRandom(2, 'computer', "weighted_random"))
        players_initial_order.append(PlayerComputerDynamicWeightedRandom(3, 'computer', "dynamic_weighted_random"))
        players_initial_order.append(PlayerComputerMyopic(4, 'computer', "heuristic"))
        players_initial_order.append(PlayerComputerRollout(5, 'computer', "rollout"))
        players_initial_order.append(PlayerHuman(6, 'human'))
        number_of_rounds = int(60 / len(players_initial_order))
        s0 = State(players_initial_order, 1, Trick(), deck, {})
        Simulation.simulate_episode(s0)
    timestamp_end = datetime.datetime.now()
    delta = timestamp_end - timestamp_start
    print(f"Time difference is {delta.total_seconds()} seconds")
    print('done')
else:
    # Queue für Nachrichtenaustausch zwischen main, simulation, player_gui und player_human
    q = queue.Queue()
    Simulation.q = q
    # setup human player
    human_player = PlayerHuman(6, 'human', q=q)
    # setup players
    players_initial_order = deque()
    players_initial_order.append(PlayerComputerRandom(1, 'computer', "random"))
    players_initial_order.append(PlayerComputerWeightedRandom(2, 'computer', "weighted_random"))
    players_initial_order.append(PlayerComputerDynamicWeightedRandom(3, 'computer', "dynamic_wr"))
    players_initial_order.append(PlayerComputerMyopic(4, 'computer', "heuristic"))
    players_initial_order.append(PlayerComputerRollout(5, 'computer', "rollout"))
    players_initial_order.append(human_player)
    # setup state
    number_of_rounds = int(60 / len(players_initial_order))
    s0 = State(players_initial_order, 1, Trick(), deck, {})
    # setup gui
    root = Tk()
    gui = PlayerGui(root, s0, human_player)
    # start simulation poll thread that distributes messages between simulation, human_player and gui
    threading.Thread(target=lambda: process_simulation_event_queue(q), name="Simulation Poll Thread").start()
    # start simulation thread
    threading.Thread(target=lambda: Simulation.simulate_episode(s0, human_player=human_player), name="Simulation Thread").start()
    # start gui in main thread
    root.mainloop()




