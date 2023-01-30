import sys
import textwrap
import threading
from tkinter import Tk, ttk, messagebox, simpledialog, Toplevel, Label, Frame
from PIL import Image, ImageTk

# list/variable must be global due to bug in ImageTk
from enum_suit import Suit

card_images_hand = {}
card_images_suit = {}
card_images_trick = []
card_image_empty = None
card_image_trump = None


class PlayerGui:

    output_q = None

    def __init__(self, master, initial_state, output_q):

        print('###__init__###')
        # self.initial_state = initial_state
        # self.human_player = human_player
        PlayerGui.output_q = output_q

        # gui stuff
        self.pad_x = 10
        self.pad_y = 10

        self.master = master
        master.title('Wizard AI')
        master.geometry("1300x800")
        master.configure(background="green")

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
        player_name_short = textwrap.shorten(str(initial_state.players_deal_order[0]), width=11, placeholder="...")
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

        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.show_game_options()
        self.setup_game(initial_state)
        # PlayerGui.output_q.put('NEW_GAME')

    def show_game_options(self):
        # game start option dialogue
        self.game_options_master = Toplevel(self.master)
        self.game_options_master.title('Game Options')
        self.game_options_master.geometry('415x150')
        self.game_options_master.configure(bg='green')

    def setup_game(self, initial_state):
        print('setup_game')
        self.player_name_labels.clear()
        self.player_bid_labels.clear()
        self.player_tricks_won_labels.clear()
        self.player_score_labels.clear()
        self.trick_frames.clear()
        self.trick_cards.clear()

        player_name_short = textwrap.shorten(str(initial_state.players_deal_order[0]), width=11, placeholder="...")
        self.trump_card_frame.configure(text=f'{player_name_short}')
        for i in range(len(initial_state.players_deal_order)):
            # stats
            player = initial_state.players_deal_order[i]
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
            player_tricks_won_label = ttk.Label(self.stats_group, text=f'{player.current_tricks_won}',
                                                style="Custom3.TLabel")
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

    def update_hand(self, state):
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

        max_cards_per_row = 7
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

    def update_trump(self, state):
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

    def update_stats(self, state):
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

    def update_trick(self, state):
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

    def update_round(self, state):
        self.round_label.configure(text=f'Round {state.round_nr}', style="Custom.TLabel")

    @staticmethod
    def update_trick_winner(state):
        winning_card = state.trick.get_highest_trick_card()
        winning_card_idx = state.trick.cards.index(winning_card)
        winning_player = state.trick.played_by[winning_card_idx]
        messagebox.showinfo(message=f'Winning card: {winning_card} from {winning_player}')

    @staticmethod
    def enter_bid():
        new_win = Tk()
        new_win.withdraw()
        # print('###enter_bid###')
        input_val = simpledialog.askinteger(title='Input', prompt='Enter your bid', parent=new_win)
        # print(f'Input value: {input_val}')
        new_win.destroy()
        return input_val

    @staticmethod
    def game_over(state):
        winning_player = max(state.players_deal_order, key=lambda x: x.current_score)
        messagebox.showinfo(message=f'Winner: {winning_player} with {winning_player.current_score}', title='Game Over.')

    @staticmethod
    def get_human_player(state):
        human_plr = None
        for plr in state.players_deal_order:
            if plr.player_type == 'human':
                human_plr = plr
        return human_plr

    @staticmethod
    def on_closing():
        print('clicked on exit')
        print(threading.enumerate())
        sys.exit()

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

    def select_suit(self):
        self.select_suit_master = Toplevel(self.master)
        self.select_suit_master.title('Select a Suit')
        self.select_suit_master.geometry('415x150')
        self.select_suit_master.configure(bg='green')
        col = 0
        for suit in Suit:
            if suit.name != 'JOKER':
                card_label = ttk.Label(self.select_suit_master, text='', image=card_images_suit[suit])  # get image of card
                card_label.grid(row=0, column=col)
                card_label.bind("<Button-1>", self.click_select_suit)
                self.widget_suit_dict[card_label] = suit
                col = col + 1

    def click_select_suit(self, event):
        print("left click suit")
        caller = event.widget
        print(caller)
        suit = self.widget_suit_dict.get(caller)
        print(suit)
        input_suit = ('INPUT_SUIT', suit)
        PlayerGui.output_q.put(input_suit)
        self.select_suit_master.destroy()
