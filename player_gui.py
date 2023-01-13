import sys
import textwrap
from tkinter import Tk, ttk, messagebox, simpledialog, Toplevel
from PIL import Image, ImageTk
from tabulate import tabulate

# list/variable must be global due to bug in ImageTk
from enum_suit import Suit

card_images_hand = {}
card_image_trump = None
card_images_trick = []
card_images_suit = {}


class PlayerGui:

    output_q = None

    def __init__(self, master, initial_state, human_player, output_q):
        print('###__init__###')
        # self.initial_state = initial_state
        # self.human_player = human_player
        PlayerGui.output_q = output_q
        # gui stuff
        self.pad_x = 10
        self.pad_y = 10

        self.master = master
        master.title('Wizard AI')
        master.geometry("1200x800")
        master.configure(background="green")

        self.mainframe = ttk.Frame(master, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0)

        self.round_label = ttk.Label(self.mainframe, text=f'Round {initial_state.round_nr}')
        self.round_label.grid(row=0, column=0)

        self.stats_group = ttk.LabelFrame(self.mainframe, text="Player Stats")
        self.stats_group.grid(padx=self.pad_x, pady=self.pad_y, row=1, column=0, sticky='N S')

        player_name_label = ttk.Label(self.stats_group, text='Playername')
        player_name_label.grid(row=0, column=0, sticky='W', pady=self.pad_y)
        player_bid_label = ttk.Label(self.stats_group, text='Bid')
        player_bid_label.grid(row=0, column=1, sticky='E', pady=self.pad_y)
        player_tricks_won_label = ttk.Label(self.stats_group, text='Tricks Won')
        player_tricks_won_label.grid(row=0, column=2, sticky='E', pady=self.pad_y)
        player_score_label = ttk.Label(self.stats_group, text='Score')
        player_score_label.grid(row=0, column=3, sticky='E', pady=self.pad_y)

        self.player_name_labels = []
        self.player_bid_labels = []
        self.player_tricks_won_labels = []
        self.player_score_labels = []
        for i in range(len(initial_state.players)):
            player = initial_state.players[i]
            player_name_label = ttk.Label(self.stats_group, text=f'{player}')
            player_name_label.grid(row=i + 1, column=0, sticky='W')
            self.player_name_labels.append(player_name_label)
            if player.current_bid == -1:
                player_bid_formatted = '-'
            else:
                player_bid_formatted = str(player.current_bid)
            player_bid_label = ttk.Label(self.stats_group, text=f'{player_bid_formatted}')
            player_bid_label.grid(row=i + 1, column=1)
            self.player_bid_labels.append(player_bid_label)
            player_tricks_won_label = ttk.Label(self.stats_group, text=f'{player.current_tricks_won}')
            player_tricks_won_label.grid(row=i + 1, column=2)
            self.player_tricks_won_labels.append(player_tricks_won_label)
            player_score_label = ttk.Label(self.stats_group, text=f'{player.current_score}')
            player_score_label.grid(row=i + 1, column=3)
            self.player_score_labels.append(player_score_label)

        self.trump_group = ttk.LabelFrame(self.mainframe, text="Trump Card", width=100)
        self.trump_group.grid(padx=self.pad_x, pady=self.pad_y, row=1, column=1, sticky='N S')

        self.trick_group = ttk.LabelFrame(self.mainframe, text='Trick Cards', width=200)
        self.trick_group.grid(padx=self.pad_x, pady=self.pad_y, row=1, column=2, sticky='N S')

        self.hand_group = ttk.LabelFrame(self.mainframe, text=f'Current hand {human_player}')
        self.hand_group.grid(padx=self.pad_x, pady=self.pad_y, row=2, column=0, columnspan=3, sticky='W')

        self.select_suit_master = None

        self.widget_card_dict = {}

        for suit in Suit:
            if suit.name == 'JOKER':
                suit_image_original = Image.open(f'gui/cards/jester.png')
            else:
                suit_image_original = Image.open(f'gui/cards/{suit}.png')
            suit_image = suit_image_original.resize((100, 145))
            card_images_suit[suit] = ImageTk.PhotoImage(suit_image)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

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
            card_label = ttk.Label(self.hand_group, text='', image=card_images_hand[card])  # get image of card
            card_label.grid(row=current_row, column=current_col)
            card_label.bind("<Button-1>", self.click_select_card)
            # card_label.bind("<Button-1>", lambda event: self.left_click(event))
            self.widget_card_dict[card_label] = card
            current_col = current_col + 1

    def update_trump(self, state):
        # print('###update trump###')
        # if state.trick.trump_suit is None:
        #     suit_image_original = Image.open(f'gui/cards/jester.png')
        # else:
        #     suit_image_original = Image.open(f'gui/cards/{state.trick.trump_suit}.png')
        # suit_image = suit_image_original.resize((100, 145))
        # global card_image_trump
        # card_image_trump = ImageTk.PhotoImage(suit_image)
        # card_label = ttk.Label(self.trump_group, text='', image=card_image_trump)  # get image of card
        # card_label.grid(row=0, column=0)
        if state.trick.trump_suit is None:
            suit = Suit(5)
        else:
            suit = state.trick.trump_suit
        card_label = ttk.Label(self.trump_group, text='', image=card_images_suit[suit])  # get image of card
        card_label.grid(row=0, column=0)

    def update_stats(self, state):
        # print('###update stats###')
        for i in range(len(state.players)):
            player = state.players[i]
            # player_name_label = ttk.Label(self.stats_group, text=f'{player}')
            # player_name_label.grid(row=i + 1, column=0, sticky='W')
            self.player_name_labels[i].configure(text=f'{player}')
            if player.current_bid == -1:
                player_bid_formatted = '-'
            else:
                player_bid_formatted = str(player.current_bid)
            # player_bid_label = ttk.Label(self.stats_group, text=f'{player_bid_formatted}')
            # player_bid_label.grid(row=i + 1, column=1)
            self.player_bid_labels[i].configure(text=f'{player_bid_formatted}')
            # player_tricks_won_label = ttk.Label(self.stats_group, text=f'{player.current_tricks_won}')
            # player_tricks_won_label.grid(row=i + 1, column=2)
            self.player_tricks_won_labels[i].configure(text=f'{player.current_tricks_won}')
            # player_score_label = ttk.Label(self.stats_group, text=f'{player.current_score}')
            # player_score_label.grid(row=i + 1, column=3)
            self.player_score_labels[i].configure(text=f'{player.current_score}')

    def update_trick(self, state):
        # print('###update trick###')
        for widgets in self.trick_group.winfo_children():
            widgets.destroy()

        card_images_trick.clear()
        # if len(state.trick.cards) == 0:
        #     card_images_trick.clear()

        for card in state.trick.cards:
            card_images_trick.append(ImageTk.PhotoImage(card.card_image))

        for i in range(len(state.trick.cards)):
            played_by = state.trick.played_by[i]
            player_name_short = textwrap.shorten(str(played_by), width=11, placeholder="...")
            card_frame = ttk.LabelFrame(self.trick_group, text=f'{player_name_short}', width=110)
            card_frame.grid(row=0, column=i, sticky='N S')
            card_label = ttk.Label(card_frame, text='', image=card_images_trick[i])  # get image of card
            card_label.grid(row=0, column=i)

        # # card_label.config(image=ImageTk.PhotoImage(card.card_image))

    def update_round(self, state):
        self.round_label.configure(text=f'Round {state.round_nr}')

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
        winning_player = max(state.players, key=lambda x: x.current_score)
        messagebox.showinfo(message=f'Winner: {winning_player} with {winning_player.current_score}', title='Game Over.')

    @staticmethod
    def get_human_player(state):
        human_plr = None
        for plr in state.players:
            if plr.player_type == 'human':
                human_plr = plr
        return human_plr

    @staticmethod
    def on_closing():
        sys.exit()

    def click_select_card(self, event):
        print("left click")
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

    def select_suit(self, event):
        self.select_suit_master = Toplevel(self.master)
        self.select_suit_master.title('Select a Suit')
        self.select_suit_master.geometry('300x150')
        self.select_suit_master.configure(bg='green')
