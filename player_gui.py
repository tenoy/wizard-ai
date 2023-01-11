import sys
import textwrap
from tkinter import Tk, ttk
from PIL import ImageTk


class PlayerGui:

    def __init__(self, master, initial_state, human_player):
        # self.initial_state = initial_state
        # self.human_player = human_player
        # gui stuff
        self.pad_x = 10
        self.pad_y = 10

        self.master = master
        master.title('Wizard AI')
        master.geometry("1050x800")
        master.configure(background="green")

        self.mainframe = ttk.Frame(master, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0)
        self.hand_group = None
        self.card_label = None

        round_label = ttk.Label(self.mainframe, text=f'Round {initial_state.round_nr}')
        round_label.grid(row=0, column=0)

        bids_group = ttk.LabelFrame(self.mainframe, text="Bids")
        bids_group.grid(padx=self.pad_x, pady=self.pad_y, row=1, column=0, sticky='N S')

        player_name_label = ttk.Label(bids_group, text='Playername')
        player_name_label.grid(row=0, column=0, sticky='W', pady=self.pad_y)
        player_bid_label = ttk.Label(bids_group, text='Bid')
        player_bid_label.grid(row=0, column=1, sticky='E', pady=self.pad_y)

        for i in range(len(initial_state.players)):
            player = initial_state.players[i]
            player_name_label = ttk.Label(bids_group, text=f'{player}')
            player_name_label.grid(row=i + 1, column=0, sticky='W')
            player_bid_label = ttk.Label(bids_group, text=f'{player.current_bid}')
            player_bid_label.grid(row=i + 1, column=1)

        trick_group = ttk.LabelFrame(self.mainframe, text='Trick Cards')
        trick_group.grid(padx=self.pad_x, pady=self.pad_y, row=1, column=1)

        # s0.trick = Trick(trump_suit=Suit.DIAMONDS,
        #                  cards=[deck[53], deck[56], deck[11], deck[12], deck[13], deck[14]],
        #                  played_by=[players_initial_order[0], players_initial_order[1], players_initial_order[2], players_initial_order[3], players_initial_order[4], players_initial_order[5]]
        #                  )

        # due to bug in ImageTk.PhotoImage, the variable name passed as an argument to the image parameter of Label must be different
        card_images_trick = []
        for card in initial_state.trick.cards:
            card_images_trick.append(ImageTk.PhotoImage(card.card_image))

        for i in range(len(initial_state.trick.cards)):
            played_by = initial_state.trick.played_by[i]
            player_name_short = textwrap.shorten(str(played_by), width=11, placeholder="...")
            card_frame = ttk.LabelFrame(trick_group, text=f'{player_name_short}', width=110)
            card_frame.grid(row=0, column=i)
            card_label = ttk.Label(card_frame, text='', image=card_images_trick[i])  # get image of card
            card_label.grid(row=0, column=i)
            # break
        # card_label.config(image=ImageTk.PhotoImage(card.card_image))

        # self.hand_group = ttk.LabelFrame(self.mainframe, text=f'Current hand {human_player}')
        # self.hand_group.grid(padx=self.pad_x, pady=self.pad_y, row=2, column=0, columnspan=2)
        #
        # card_images_hand = []
        # for card in human_player.current_hand:
        #     card_images_hand.append(ImageTk.PhotoImage(card.card_image))
        #
        # max_cards_per_row = 7
        # current_row = 0
        # current_col = 0
        # for i in range(len(human_player.current_hand)):
        #     if current_col >= max_cards_per_row:
        #         current_row = current_row + 1
        #         current_col = 0
        #     self.card_label = ttk.Label(self.hand_group, text='', image=card_images_hand[i])  # get image of card
        #     self.card_label.grid(row=current_row, column=current_col)
        #     current_col = current_col + 1

        # Thread mit funktion für polling des queues von player_human aufmachen
        # Gui entsprechend der Nachrichten in der Queue anpassen

        # start_btn = Button(root, text="Start", command=lambda: Simulation.simulate_episode(s0, number_of_rounds))
        # start_btn.grid(row=0, column=0, padx=10, pady=10)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_hand(self, state):
        human_player = self.get_human_player(state)
        self.hand_group = ttk.LabelFrame(self.mainframe, text=f'Current hand {human_player}')
        self.hand_group.grid(padx=self.pad_x, pady=self.pad_y, row=2, column=0, columnspan=2)
        card_images_hand = []
        for card in human_player.current_hand:
            card_images_hand.append(ImageTk.PhotoImage(card.card_image))
        max_cards_per_row = 7
        current_row = 0
        current_col = 0
        for i in range(len(human_player.current_hand)):
            if current_col >= max_cards_per_row:
                current_row = current_row + 1
                current_col = 0
            self.card_label = ttk.Label(self.hand_group, text='', image=card_images_hand[i])  # get image of card
            self.card_label.grid(row=current_row, column=current_col)
            current_col = current_col + 1

    def update_trump(self):
        pass

    def update_bids(self):
        pass

    def update_trick(self):
        pass

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
