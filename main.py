import queue
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

def process_simulation_event_queue():
    while True:
        # time.sleep(0.05)
        try:
            # print(f'poll: call get {input_q.queue}')
            msg = input_q.get(block=True, timeout=0.05)
            if msg == "UPDATE_HAND":
                gui.update_hand()
                #update_hand()
                input_q.task_done()
            elif msg == "UPDATE_TRUMP":
                # print('update trump')
                gui.update_trump()
                input_q.task_done()
            elif msg == "UPDATE_STATS":
                # print('update stats')
                gui.update_stats()
                input_q.task_done()
            elif msg == "UPDATE_TRICK":
                # print('update trick')
                gui.update_trick()
                input_q.task_done()
            elif msg == "UPDATE_ROUND":
                # print('update round')
                gui.update_round()
                input_q.task_done()
            elif msg == "UPDATE_TRICK_WINNER":
                # print('update trick winner')
                gui.update_trick_winner()
                input_q.task_done()
            elif msg == "ENTER_BID":
                # print('poll: call enter bid gui')
                gui.enter_bid()
                # bid = root.after(0, gui.enter_bid)
                # print(f'poll: bid value: {bid}')
                # print(f'poll: call task done')
                # print(f'poll:  {q.queue}')
                input_q.task_done()
                # print('poll: putting INPUT_BID')
                # input_bid = ('INPUT_BID', bid)
                # output_q.put(input_bid)
                # print(f'poll:  {input_q.queue}')
                # print('poll: call join')
                # output_q.join()
            elif msg == "GAME_OVER":
                gui.game_over()
                input_q.task_done()
            elif msg == "INVALID_CARD":
                gui.invalid_card()
                input_q.task_done()
            elif msg == "INVALID_INPUT":
                gui.invalid_input()
                input_q.task_done()
            elif msg == "INVALID_BID":
                gui.invalid_bid()
                input_q.task_done()
            elif msg == "SELECT_SUIT":
                gui.select_suit()
                input_q.task_done()
        except queue.Empty:
            # print(f'poll: empty {input_q.queue}')
            time.sleep(0.05)


# program mode is either 'game' (with human player) or 'simulation' (only computers)
global program_mode
program_mode = 'simulation'

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
    result_list = []
    win_count_player = {}
    for i in range(0, 100):
        players_initial_order = deque()
        # players_initial_order.append(PlayerComputerRollout(1, 'computer', "rollout"))
        players_initial_order.append(PlayerComputerRandom(1, 'computer', "random"))
        players_initial_order.append(PlayerComputerWeightedRandom(2, 'computer', "weighted_random"))
        players_initial_order.append(PlayerComputerDynamicWeightedRandom(3, 'computer', "dynamic_weighted_random"))
        players_initial_order.append(PlayerComputerMyopic(4, 'computer', "heuristic"))
        players_initial_order.append(PlayerComputerRollout(5, 'computer', "rollout"))
        s0 = State(players_deal_order=players_initial_order, round_nr=1, trick=Trick(trick_nr=1), deck=deck, bids={})
        result = Simulation.simulate_episode(s0)
        result_list.append(result)
        print(f'Game {i} done')

    for result_tuple in result_list:
        if result_tuple[1] in win_count_player:
            win_count_player[result_tuple[1]] += 1
        else:
            win_count_player[result_tuple[1]] = 1

    for key, value in win_count_player.items():
        print(f"{key}: {value}")

    timestamp_end = datetime.datetime.now()
    delta = timestamp_end - timestamp_start
    delta_str = str(delta).split('.')[0]
    print(f"Time difference is {delta_str}")
    print('done')
else:
    # Queues für Duplex Nachrichtenaustausch zwischen main, simulation, player_gui und player_human
    input_q = queue.Queue()
    output_q = queue.Queue()
    # input_q = alle nachrichten zum Simulation Poll Thread, ouput_q = alle nachrichten aus Simulation Poll Thread
    Simulation.input_q = input_q
    Simulation.output_q = output_q
    # setup gui
    root = Tk()

    gui = PlayerGui(root, deck, input_q, output_q)
    # start simulation poll thread that distributes messages between simulation, human_player and gui
    threading.Thread(target=lambda: process_simulation_event_queue(), name="Simulation Poll Thread", daemon=True).start()
    # start simulation thread
    # threading.Thread(target=lambda: Simulation.simulate_episode(s0, human_player=human_player), name="Simulation Thread", daemon=True).start()
    # start gui in main thread
    root.mainloop()




