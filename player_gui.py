import sys
import textwrap
import threading
from tkinter import ttk, messagebox, Toplevel, Label, Frame, Menu, Listbox, Button, END, Entry
from PIL import Image, ImageTk
from enum_suit import Suit
from player_human import PlayerHuman
from policies.player_computer_dynamic_weighted_random import PlayerComputerDynamicWeightedRandom
from policies.player_computer_myopic import PlayerComputerMyopic
from policies.player_computer_random import PlayerComputerRandom
from policies.player_computer_rollout import PlayerComputerRollout
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom
from simulation import Simulation
from state import State
from trick import Trick

# list/variable must be global due to bug in ImageTk

card_images_hand = {}
card_images_suit = {}
card_images_trick = []
card_image_empty = None
card_image_trump = None


class PlayerGui:

    output_q = None
    input_q = None

    def __init__(self, master, deck, input_q, output_q):

        print('###__init__###')
        # self.initial_state = initial_state
        # self.human_player = human_player
        PlayerGui.output_q = output_q
        PlayerGui.input_q = input_q
        self.deck = deck
        self.human_player = None

        # gui stuff
        self.pad_x = 10
        self.pad_y = 10

        self.master = master
        master.title('Wizard AI')
        master.geometry("1300x800")
        master.configure(background="green")

        self.x_pos = self.master.winfo_x()
        self.y_pos = self.master.winfo_y()

        menu = Menu(master)
        master.config(menu=menu)
        main_menu = Menu(menu)
        menu.add_cascade(label='Menu', menu=main_menu)
        main_menu.add_command(label='New Game', command=self.show_game_options)

        self.style_root = ttk.Style(master)
        self.style_root.theme_use("default")
        self.style_frames = ttk.Style(master)
        self.style_frames.configure("Custom.TFrame", background="green")
        self.style_frames.configure("Custom2.TFrame", background="white")
        self.style_labels = ttk.Style(master)
        self.style_labels.configure("Custom.TLabel", background="green", foreground="white", font="Arial 22")
        self.style_labels.configure("Custom2.TLabel", background="green", foreground="white", font="Arial 12 underline")
        self.style_labels.configure("Custom3.TLabel", background="green", foreground="white", font="Arial 11")
        self.style_label_frames = ttk.Style(master)
        self.style_label_frames.configure("Custom.TLabelframe", background="green", foreground="white", relief="flat", padding=10)
        self.style_label_frames.configure("Custom2.TLabelframe", background="green", foreground="white", relief="flat")
        self.style_label_frames.configure("Custom.TLabelframe.Label", background="green", foreground="white", font="Arial 14")
        self.style_label_frames.configure("Custom2.TLabelframe.Label", background="green", foreground="white", font="Arial 11")

        self.mainframe = ttk.Frame(master, padding="3 3 12 12", style="Custom.TFrame")
        self.mainframe.pack()

        self.round_label = ttk.Label(self.mainframe, style="Custom.TLabel")
        self.round_label.grid(row=0, column=0, columnspan=3)

        self.stats_group_border = ttk.Frame(self.mainframe, style="Custom2.TFrame")
        self.stats_group_border.grid(padx=self.pad_x, pady=self.pad_y, row=1, column=0, sticky='N S')
        self.stats_group = ttk.LabelFrame(self.stats_group_border, text="Player Stats", style="Custom.TLabelframe")
        self.stats_group.pack(padx=2, pady=2, fill='y', expand=True)
        # self.stats_group.grid(padx=2, pady=2, row=0, column=0, sticky='N S E W')

        for suit in Suit:
            if suit.name == 'JOKER':
                suit_image_original = Image.open(f'gui/cards/jester.png')
            else:
                suit_image_original = Image.open(f'gui/cards/{suit}.png')
            suit_image = suit_image_original.resize((100, 145))
            card_images_suit[suit] = ImageTk.PhotoImage(suit_image)

        empty_card_image_original = Image.open(f'gui/cards/empty.png')
        empty_card_image = empty_card_image_original.resize((100, 145))
        global card_image_empty
        card_image_empty = ImageTk.PhotoImage(empty_card_image)

        self.trump_group_border = ttk.Frame(self.mainframe, style="Custom2.TFrame")
        self.trump_group_border.grid(padx=0, pady=self.pad_y, row=1, column=1, sticky='S N')
        self.trump_group = ttk.LabelFrame(self.trump_group_border, text="Trump Suit", style="Custom.TLabelframe")
        self.trump_group.pack(padx=2, pady=2, fill='y', expand=True)
        # player_name_short = textwrap.shorten(str(initial_state.players_deal_order[0]), width=11, placeholder="...")
        self.trump_card_frame = ttk.LabelFrame(self.trump_group, style="Custom2.TLabelframe")
        self.trump_card_frame.pack()
        # self.trump_group.grid(padx=2, pady=2, row=0, column=0, sticky='N S')
        self.trump_card = ttk.Label(self.trump_card_frame, image=card_image_empty, style="Custom3.TLabel")
        self.trump_card.pack()

        self.trick_group_border = ttk.Frame(self.mainframe, style="Custom2.TFrame")
        self.trick_group_border.grid(padx=self.pad_x, pady=self.pad_y, row=1, column=2, sticky='N S E W')
        # self.trick_group_border.grid_propagate(False)
        self.trick_group = ttk.LabelFrame(self.trick_group_border, text='Trick Cards', style="Custom.TLabelframe")
        self.trick_group.pack(padx=2, pady=2, fill='both', expand=True)
        # self.trick_group.grid(padx=2, pady=2, row=0, column=0, sticky='N S E W')

        player_name_label = ttk.Label(self.stats_group, text='Playername', style="Custom2.TLabel")
        player_name_label.grid(row=0, column=0, sticky='W', pady=self.pad_y)
        player_bid_label = ttk.Label(self.stats_group, text='Bid', style="Custom2.TLabel")
        player_bid_label.grid(row=0, column=1, sticky='E', pady=self.pad_y, padx=self.pad_x)
        player_tricks_won_label = ttk.Label(self.stats_group, text='Tricks Won', style="Custom2.TLabel")
        player_tricks_won_label.grid(row=0, column=2, sticky='E', pady=self.pad_y, padx=self.pad_x)
        player_score_label = ttk.Label(self.stats_group, text='Score', style="Custom2.TLabel")
        player_score_label.grid(row=0, column=3, sticky='E', pady=self.pad_y, padx=self.pad_x)

        self.player_name_labels = []
        self.player_bid_labels = []
        self.player_tricks_won_labels = []
        self.player_score_labels = []
        self.trick_frames = []
        self.trick_cards = []

        self.hand_group_border = ttk.Frame(self.mainframe, style="Custom2.TFrame")
        self.hand_group_border.grid(padx=self.pad_x, pady=self.pad_y, row=2, column=0, columnspan=3, sticky='W')
        self.hand_group = ttk.LabelFrame(self.hand_group_border, text=f'Your Cards', style="Custom.TLabelframe")
        self.hand_group.grid(padx=2, pady=2, row=0, column=0, sticky='W')

        self.select_suit_master = None
        self.game_options_master = None

        self.widget_card_dict = {}
        self.widget_suit_dict = {}

        self.entry_human_player_name = None
        self.add_computer_list = None
        self.selected_computer_list = None

        self.state = None
        self.simulation_thread = None

        self.enter_bid_window = None
        self.enter_bid_entry = None
        self.enter_bid_button = None

        self.game_over_window = None

        master.protocol("WM_DELETE_WINDOW", self.on_closing_root)
        self.show_game_options()

    def show_game_options(self):
        # game start option dialogue
        if self.state is None:
            self.master.withdraw()
        self.game_options_master = Toplevel(self.master)
        self.game_options_master.title('Game Options')
        self.game_options_master.geometry('600x400')
        self.game_options_master.geometry("+%d+%d" % (self.x_pos + 350, self.y_pos + 200))
        # self.game_options_master.grab_set()
        self.game_options_master.focus_force()

        mainframe_game_options = ttk.Frame(self.game_options_master, style="Custom.TFrame", relief='solid')
        mainframe_game_options.pack()

        # input for human player name
        frame_human_player_name = ttk.Frame(mainframe_game_options, style="Custom.TFrame")
        frame_human_player_name.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='W')
        label_human_player_name = ttk.Label(frame_human_player_name, text=f'Enter Your Name: ', style="Custom3.TLabel")
        label_human_player_name.pack(side='left')
        self.entry_human_player_name = Entry(frame_human_player_name)
        self.entry_human_player_name.insert(END, 'Wizard Player')
        self.entry_human_player_name.pack(side='left')

        # list with different levels of computer players
        frame_add_computer = ttk.Frame(mainframe_game_options, style="Custom.TFrame")
        frame_add_computer.grid(row=1, column=0, padx=10, pady=10)
        add_computer_label = ttk.Label(frame_add_computer, text="Add Computer Player(s)", style="Custom3.TLabel")
        add_computer_label.pack(padx=10)
        self.add_computer_list = Listbox(frame_add_computer, exportselection=True, width=35, height=15)
        self.add_computer_list.pack(padx=10, pady=10)
        self.add_computer_list.insert(0, 'Idiot')
        self.add_computer_list.insert(1, 'Easy')
        self.add_computer_list.insert(2, 'Medium')
        self.add_computer_list.insert(3, 'Hard')
        self.add_computer_list.insert(4, 'Expert')

        # Buttons for adding and removing computer players
        frame_buttons = ttk.Frame(mainframe_game_options, style="Custom.TFrame")
        frame_buttons.grid(row=1, column=1, padx=10, pady=10)
        add_computer_button = Button(frame_buttons, text='+', command=self.add_computer_player, height=2, width=5)
        add_computer_button.pack(pady=10)
        remove_computer_button = Button(frame_buttons, text='-', command=self.remove_computer_player, height=2, width=5)
        remove_computer_button.pack(pady=10)

        # list with selected computer players
        frame_selected_computer = ttk.Frame(mainframe_game_options, style="Custom.TFrame")
        frame_selected_computer.grid(row=1, column=2, padx=10, pady=10)
        selected_computer_label = ttk.Label(frame_selected_computer, text="Selected Computer Player(s)", style="Custom3.TLabel")
        selected_computer_label.pack(padx=10)
        self.selected_computer_list = Listbox(frame_selected_computer, exportselection=True, width=35, height=15)
        self.selected_computer_list.pack(padx=10, pady=10)

        # start game button
        start_game_button = Button(mainframe_game_options, text='Start Game!', command=self.start_game)
        start_game_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def add_computer_player(self):
        selection = self.add_computer_list.curselection()
        if len(selection) > 0:
            selection_computer = self.add_computer_list.get(selection)
            print(f'added computer: {selection_computer}')
            if self.selected_computer_list.size() > 4:
                messagebox.showinfo(message=f'You cannot add more than 5 players')
            else:
                self.selected_computer_list.insert(END, selection_computer)

    def remove_computer_player(self):
        selection = self.selected_computer_list.curselection()
        if len(selection) > 0:
            self.selected_computer_list.delete(self.selected_computer_list.curselection())

    def start_game(self):
        if self.selected_computer_list.size() < 2:
            messagebox.showinfo(message=f'You have to add at least 2 players')
        else:
            self.setup_game()
            print(f'{self.master.state()}')
            self.master.deiconify()
            print(f'{self.master.state()}')
            print(f'{threading.enumerate()}')

    def setup_game(self):
        print('setup_game')

        players_initial_order = list()
        self.human_player = PlayerHuman(1, 'human', player_name='Wizard Player', input_q=PlayerGui.input_q, output_q=PlayerGui.output_q)
        human_player_name = self.entry_human_player_name.get()
        self.human_player.name = human_player_name
        players_initial_order.append(self.human_player)

        for idx, entry in enumerate(self.selected_computer_list.get(0, END)):
            print(f'{entry}')
            nr = idx+2
            if entry == 'Idiot':
                players_initial_order.append(PlayerComputerRandom(nr, 'computer', entry))
            if entry == 'Easy':
                players_initial_order.append(PlayerComputerWeightedRandom(nr, 'computer', entry))
            if entry == 'Medium':
                players_initial_order.append(PlayerComputerDynamicWeightedRandom(nr, 'computer', entry))
            if entry == 'Hard':
                players_initial_order.append(PlayerComputerMyopic(nr, 'computer', entry))
            if entry == 'Expert':
                players_initial_order.append(PlayerComputerRollout(nr, 'computer', entry))

        self.state = State(players_initial_order, 1, Trick(), self.deck, {})

        if self.simulation_thread is not None:
            PlayerGui.output_q.put('GAME_RESTART')
            self.simulation_thread.join()
        self.simulation_thread = threading.Thread(target=lambda: Simulation.simulate_episode(self.state, human_player=self.human_player), name="Simulation Thread", daemon=True)
        with PlayerGui.input_q.mutex:
            PlayerGui.input_q.queue.clear()
        with PlayerGui.output_q.mutex:
            PlayerGui.output_q.queue.clear()
        print(f'Input q: {PlayerGui.input_q.queue}')
        print(f'Output q: {PlayerGui.output_q.queue}')
        self.simulation_thread.start()

        # self.player_name_labels.clear()
        for i in range(len(self.player_name_labels)):
            print('destroying old widgets')
            self.player_name_labels[i].destroy()
            self.player_bid_labels[i].destroy()
            self.player_tricks_won_labels[i].destroy()
            self.player_score_labels[i].destroy()
            self.trick_frames[i].destroy()
            self.trick_cards[i].destroy()

        self.player_name_labels.clear()
        self.player_bid_labels.clear()
        self.player_tricks_won_labels.clear()
        self.player_score_labels.clear()
        self.trick_frames.clear()
        self.trick_cards.clear()

        player_name_short = textwrap.shorten(str(self.state.players_deal_order[0]), width=11, placeholder="...")
        self.trump_card_frame.configure(text=f'{player_name_short}')
        for i in range(len(self.state.players_deal_order)):
            # stats
            player = self.state.players_deal_order[i]
            player_name_label = ttk.Label(self.stats_group, text=f'{player}', style="Custom3.TLabel")
            player_name_label.grid(row=i + 1, column=0, sticky='W')
            self.player_name_labels.append(player_name_label)
            if player.current_bid == -1:
                player_bid_formatted = '-'
            else:
                player_bid_formatted = str(player.current_bid)
            player_bid_label = ttk.Label(self.stats_group, text=f'{player_bid_formatted}', style="Custom3.TLabel")
            player_bid_label.grid(row=i + 1, column=1)
            self.player_bid_labels.append(player_bid_label)
            player_tricks_won_label = ttk.Label(self.stats_group, text=f'{player.current_tricks_won}', style="Custom3.TLabel")
            player_tricks_won_label.grid(row=i + 1, column=2)
            self.player_tricks_won_labels.append(player_tricks_won_label)
            player_score_label = ttk.Label(self.stats_group, text=f'{player.current_score}', style="Custom3.TLabel")
            player_score_label.grid(row=i + 1, column=3)
            self.player_score_labels.append(player_score_label)

            # trick
            player_name_short = textwrap.shorten(str(player), width=11, placeholder="...")
            card_frame = ttk.LabelFrame(self.trick_group, text=f'{player_name_short}', style="Custom2.TLabelframe")
            card_frame.grid(row=0, column=i, sticky='N S')
            # card_frame.grid_rowconfigure(0, weight=1)
            self.trick_frames.append(card_frame)
            card_label = ttk.Label(self.trick_frames[i], image=card_image_empty, style="Custom3.TLabel")
            card_label.pack(fill='both', expand=True)
            # card_label.grid(row=0, column=0, sticky='N S E W')
            self.trick_cards.append(card_label)
        self.game_options_master.destroy()

    def update_hand(self):
        state = self.state
        # print('###update hand###')
        self.widget_card_dict.clear()
        human_player = self.get_human_player(state)
        if len(human_player.played_cards) == 0:
            card_images_hand.clear()
        else:
            for card in human_player.played_cards:
                print(f'delete card: {card}')
                if card_images_hand.get(card) is not None:
                    del card_images_hand[card]

        # self.hand_group = ttk.LabelFrame(self.mainframe, text=f'Current hand {human_player}')
        # self.hand_group.grid(padx=self.pad_x, pady=self.pad_y, row=2, column=0, columnspan=2)
        # card_images_hand = []
        for card in human_player.current_hand:
            card_images_hand[card] = ImageTk.PhotoImage(card.card_image)

        max_cards_per_row = 8
        current_row = 0
        current_col = 0
        for i in range(len(human_player.current_hand)):
            card = human_player.current_hand[i]
            if current_col >= max_cards_per_row:
                current_row = current_row + 1
                current_col = 0
            card_label = ttk.Label(self.hand_group, text='', image=card_images_hand[card], style="Custom3.TLabel")  # get image of card
            card_label.grid(row=current_row, column=current_col)
            card_label.bind("<Button-1>", self.click_select_card)
            # card_label.bind("<Button-1>", lambda event: self.left_click(event))
            self.widget_card_dict[card_label] = card
            current_col = current_col + 1

    def update_trump(self):
        state = self.state
        if state.trick.trump_suit is None:
            # Suit 5 is the Joker suit
            suit = Suit(5)
        else:
            suit = state.trick.trump_suit
        player_name_short = textwrap.shorten(str(state.players_deal_order[0]), width=11, placeholder="...")
        self.trump_card_frame.configure(text=f'{player_name_short}')
        self.trump_card.configure(image=card_images_suit[suit], style="Custom3.TLabel")
        # card_label = ttk.Label(self.trump_group, image=card_images_suit[suit], style="Custom3.TLabel")  # get image of card
        # card_label.pack()
        # card_label.grid(row=0, column=0, pady=0, sticky='S N')

    def update_stats(self):
        state = self.state
        for i in range(len(state.players_bid_order)):
            player = state.players_bid_order[i]
            self.player_name_labels[i].configure(text=f'{player}')
            if player.current_bid == -1:
                player_bid_formatted = '-'
            else:
                player_bid_formatted = str(player.current_bid)
            self.player_bid_labels[i].configure(text=f'{player_bid_formatted}')
            self.player_tricks_won_labels[i].configure(text=f'{player.current_tricks_won}')
            self.player_score_labels[i].configure(text=f'{player.current_score}')

    def update_trick(self):
        state = self.state
        # print('###update trick###')
        # for widgets in self.trick_group.winfo_children():
        #     widgets.destroy()
        print(f'card_images_size: {len(card_images_trick)}')
        for i in range(len(state.players_play_order)):
            player = state.players_play_order[i]
            player_name_short = textwrap.shorten(str(player), width=11, placeholder="...")
            self.trick_frames[i].configure(text=f'{player_name_short}', style="Custom2.TLabelframe")
            self.trick_cards[i].configure(image=card_image_empty, style="Custom3.TLabel")
            # card_frame = ttk.LabelFrame(self.trick_group, text=f'{player_name_short}', width=110)

        start_index = len(card_images_trick)
        if start_index > len(state.trick.cards):
            print("###########################################delete all cards in trick")
            card_images_trick.clear()

        for i in range(start_index, len(state.trick.cards)):
            card_images_trick.append(ImageTk.PhotoImage(state.trick.cards[i].card_image))

        for i in range(len(state.trick.cards)):
            self.trick_cards[i].configure(image=card_images_trick[i], style="Custom3.TLabel")

    def update_round(self):
        state = self.state
        self.round_label.configure(text=f'Round {state.round_nr}', style="Custom.TLabel")

    def update_trick_winner(self):
        winning_card = self.state.trick.get_highest_trick_card()
        winning_card_idx = self.state.trick.cards.index(winning_card)
        winning_player = self.state.trick.played_by[winning_card_idx]
        messagebox.showinfo(message=f'Winning card: {winning_card} from {winning_player}')

    def enter_bid(self):
        if self.enter_bid_window is None:
            self.enter_bid_window = Toplevel(self.master)
            self.enter_bid_window.title('Enter Bid!')
            self.enter_bid_window.geometry('200x100')
            self.enter_bid_window.geometry("+%d+%d" % (self.x_pos + 550, self.y_pos + 550))
            self.enter_bid_window.wm_transient(self.master)
            self.enter_bid_window.bind('<Return>', self.input_bid)

            self.enter_bid_entry = Entry(self.enter_bid_window)
            self.enter_bid_entry.pack(pady=10)
            self.enter_bid_button = Button(self.enter_bid_window, text='Bid', command=self.input_bid, height=1, width=6)
            self.enter_bid_button.pack(pady=10)
        else:
            self.enter_bid_window.deiconify()
            self.enter_bid_entry.delete(0, END)
        self.enter_bid_entry.focus_force()
        self.enter_bid_window.protocol("WM_DELETE_WINDOW", self.on_closing_bid)

    def input_bid(self, event=None):
        print(f'input_bid')
        bid = self.enter_bid_entry.get()
        input_bid = ('INPUT_BID', bid)
        PlayerGui.output_q.put(input_bid)
        # self.enter_bid_window.destroy()
        self.enter_bid_window.withdraw()

    def game_over(self):
        print(f'############ Game Over')
        winning_player = max(self.state.players_deal_order, key=lambda x: x.current_score)
        self.game_over_window = Toplevel(self.master)
        self.game_over_window.title('Game Over!')
        self.game_over_window.geometry('300x100')
        self.game_over_window.geometry("+%d+%d" % (self.x_pos + 500, self.y_pos + 350))
        self.game_over_window.wm_transient(self.master)
        self.game_over_window.focus_force()
        game_over_mainframe = Frame(self.game_over_window)
        game_over_mainframe.pack(pady=(10, 2))
        winner_label = Label(game_over_mainframe, text=f'Winner: {winning_player} with {winning_player.current_score} points')
        winner_label.pack(padx=10, pady=10)
        buttons_frame = Frame(game_over_mainframe)
        buttons_frame.pack(padx=10, pady=10)
        exit_button = Button(buttons_frame, text='Exit', command=self.on_closing_root, height=2, width=9)
        exit_button.pack(padx=10, side='left')
        new_game_button = Button(buttons_frame, text='New Game', command=self.start_new_game, height=2, width=9)
        new_game_button.pack(padx=10, side='right')
        # messagebox.showinfo(message=f'Winner: {winning_player} with {winning_player.current_score}', title='Game Over.')

    def start_new_game(self):
        self.game_over_window.destroy()
        self.show_game_options()

    @staticmethod
    def get_human_player(state):
        human_plr = None
        for plr in state.players_deal_order:
            if plr.player_type == 'human':
                human_plr = plr
        return human_plr

    @staticmethod
    def on_closing_root():
        print('clicked on exit')
        print(threading.enumerate())
        sys.exit()

    def on_closing_bid(self):
        print('clicked on bid exit')
        messagebox.showinfo(message='You need to input a bid!', title='Exit Bid')
        self.enter_bid_entry.focus_force()
        # self.enter_bid()

    def on_closing_suit(self):
        print('clicked on suit exit')
        messagebox.showinfo(message='You need to select a suit!', title='Exit Suit')
        self.select_suit_master.focus_force()

    def click_select_card(self, event):
        print("left click card")
        caller = event.widget
        print(caller)
        card = self.widget_card_dict.get(caller)
        input_card = ('INPUT_CARD', card)
        PlayerGui.output_q.put(input_card)

    @staticmethod
    def invalid_card():
        messagebox.showinfo(message='You have at least one card that fits the suit. You must either play a card with fitting suit or a joker card.', title='Invalid Card')

    @staticmethod
    def invalid_bid():
        messagebox.showinfo(message='With your bid the sum of bids equals the round number. The sum of bids is not allowed to match the round number.',title='Invalid Bid')

    @staticmethod
    def invalid_input():
        messagebox.showinfo(message='Invalid input. Input must be a positive number.', title='Invalid Input')

    def select_suit(self):
        self.select_suit_master = Toplevel(self.master)
        self.select_suit_master.title('Select a Suit')
        self.select_suit_master.geometry('415x150')
        self.select_suit_master.configure(bg='green')
        self.select_suit_master.geometry("+%d+%d" % (self.x_pos + 445, self.y_pos + 325))
        self.select_suit_master.wm_transient(self.master)
        self.select_suit_master.focus_force()
        col = 0
        for suit in Suit:
            if suit.name != 'JOKER':
                card_label = ttk.Label(self.select_suit_master, text='', image=card_images_suit[suit])  # get image of card
                card_label.grid(row=0, column=col)
                card_label.bind("<Button-1>", self.click_select_suit)
                self.widget_suit_dict[card_label] = suit
                col = col + 1
        self.select_suit_master.protocol("WM_DELETE_WINDOW", self.on_closing_suit)

    def click_select_suit(self, event):
        print("left click suit")
        caller = event.widget
        print(caller)
        suit = self.widget_suit_dict.get(caller)
        print(suit)
        input_suit = ('INPUT_SUIT', suit)
        PlayerGui.output_q.put(input_suit)
        self.select_suit_master.destroy()
