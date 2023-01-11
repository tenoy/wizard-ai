import queue
import sys
import textwrap
import threading
import time
from collections import deque
from tkinter import Tk

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


def process_simulation_event_queue(q):
    while True:
        time.sleep(1)
        try:
            msg = q.get(block=False)
            if msg == "UPDATE_HAND":
                print('test received')
                gui.update_hand(s0)
                q.task_done()
            elif msg == "UPDATE_TRUMP":
                gui.update_trump()
                q.task_done()
            elif msg == "UPDATE_BIDS":
                gui.update_bids()
                q.task_done()
            elif msg == "UPDATE_TRICK":
                gui.update_trick()
                q.task_done()
        except queue.Empty:
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
    # setup human player
    human_player = PlayerHuman(6, 'human')
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
    # Queue für Nachrichtenaustausch zwischen main thread, player human und simulation
    q = queue.Queue()
    Simulation.q = q
    root = Tk()
    gui = PlayerGui(root, s0, human_player)
    threading.Thread(target=lambda: process_simulation_event_queue(q), name="Simulation Poll Thread").start()
    threading.Thread(target=lambda: Simulation.simulate_episode(s0, human_player=human_player), name="Simulation Thread").start()
    root.mainloop()




