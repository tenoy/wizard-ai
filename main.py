import random
from collections import deque
from random import sample
from card import Card
from enum_rank import Rank
from enum_suit import Suit
from player_computer import PlayerComputer
from player_human import PlayerHuman
from state import State


def get_leading_suit(trick_cards):
    leading_suit = None
    for card in trick_cards:
        # if jester is played first, then the next card will be the leading suit,
        # except if it's also a jester
        if card.rank != Rank.JESTER:
            leading_suit = card.suit
            return leading_suit
    return leading_suit


def get_highest_card_in_trick(trick_cards, trump_suit, leading_suit):
    # case with wizard in trick -> first wizard wins
    for card in trick_cards:
        if card.rank == Rank.WIZARD:
            return card
    # case with trump in trick -> the highest trump card wins
    if trump_suit is not None:
        trump_cards = []
        for card in trick_cards:
            if card.suit == trump_suit:
                trump_cards.append(card)

        if len(trump_cards) == 1:
            return trump_cards[0]
        elif len(trump_cards) > 1:
            return max(trump_cards)

    # case without wizard or trump card
    # leading_suit = get_leading_suit(trick_cards)
    leading_suit_cards = []
    if leading_suit is not None:
        for card in trick_cards:
            if card.suit == leading_suit:
                leading_suit_cards.append(card)

        if len(leading_suit_cards) == 1:
            return leading_suit_cards[0]
        else:
            return max(leading_suit_cards)
    else:
        # case with only jesters
        return trick_cards[0]  # the first jester wins

def simulate_episode(state):
    players_game_order = state.players
    deck = state.deck
    number_of_rounds = int(60 / len(players_game_order))
    for i in range(1, number_of_rounds+1, 1):
        # create a new deque for 'in round order'
        players = deque(players_game_order)
        # Sample cards from deck
        if i == number_of_rounds:
            sampled_cards = sample(deck, i*len(players))
        else:
            sampled_cards = sample(deck, i*len(players)+1)
        # Each player gets their share of sampled cards
        bids = {}
        start_idx = 0
        # testing_card = 55
        for player in players:
            player.current_hand = sampled_cards[start_idx:start_idx+i]
            # player.current_hand = [deck[testing_card]]
            start_idx = start_idx + i
            # testing_card = testing_card + 1

        # Sample trump suit (except in last round)
        trump_card = None
        trump_suit = None
        if i < number_of_rounds:
            trump_card = sampled_cards[len(sampled_cards)-1]
            # trump_card = Card(Suit.JOKER, Rank.WIZARD) # for testing
            trump_suit = trump_card.suit
            if trump_suit == Suit.JOKER:
                if trump_card.rank == Rank.WIZARD:
                    trump_suit = players[0].select_suit()
                else:
                    trump_suit = None

        # Place bids
        for player in players:
            player.current_bid = player.make_bid(i, bids, players, trump_suit)
            bids[player] = player.current_bid

        # Each player plays a card one after another in each trick j of round i
        for j in range(0, i, 1):
            trick = []
            leading_suit = None
            for player in players:
                played_card = player.play(trick, leading_suit, trump_suit, bids)
                trick.append(played_card)
                if leading_suit is None:
                    leading_suit = get_leading_suit(trick)
            highest_card = get_highest_card_in_trick(trick, trump_suit, leading_suit)
            win_count_card = winning_cards.setdefault(highest_card, 0)
            winning_cards[highest_card] = win_count_card + 1
            # evaluate trick winning player
            winning_player = None
            rotate_by = -1
            for k in range(0, len(players), 1):
                player = players[k]
                if player.played_card == highest_card:
                    player.current_tricks_won = player.current_tricks_won + 1
                    winning_player = player
                    rotate_by = len(players) - k
            for player in players:
                if player.player_type == 'human':
                    print('Trump suit: ' + str(trump_suit))
                    print('Cards in trick: ', end=' ')
                    print(*trick, sep=', ')
                    print('Winning card: ' + str(highest_card) + ' from Player ' + str(winning_player.number))
            players.rotate(rotate_by)

        # Calc score for each player and reset player hands etc
        for player in players_game_order:
            if player.current_bid == player.current_tricks_won:
                player.current_score = player.current_score + 20 + player.current_tricks_won * 10
            else:
                player.current_score = player.current_score - (abs(player.current_tricks_won - player.current_bid)) * 10
            player.current_tricks_won = 0
            player.current_bid = -1
            player.current_hand = []
            player.played_card = None
            print(str(player) + ', Score: ' + str(player.current_score))

        # next round another player starts
        players_game_order.rotate(1)
        print('Round ' + str(i) + ' done')
    # evaluate winning player
    highest_score = -10000000000
    highest_score_player = None
    for player in players:
        if player.current_score > highest_score:
            highest_score = player.current_score
            highest_score_player = player
        elif player.current_score == highest_score:
            rnd = random.randint(0, 1)
            if rnd == 0:
                highest_score = player.current_score
                highest_score_player = player
        player.current_score = 0

    highest_score_player.games_won = highest_score_player.games_won + 1
    for player in state.players:
        print(str(player) + ', Games won: ' + str(player.games_won))


deck = []
for i in range(1, 5, 1):
    for j in range(2, 15, 1):
        c = Card(Suit(i), Rank(j))
        deck.append(c)
        #print(c)

for i in range(1, 5, 1):
    c = Card(Suit.JOKER, Rank.JESTER)
    deck.append(c)
    #print(c)

for i in range(1, 5, 1):
    c = Card(Suit.JOKER, Rank.WIZARD)
    deck.append(c)
    #print(c)

# put in game class or something similar
number_of_players = 2
players_initial_order = deque()
for i in range(1, number_of_players+1, 1):
    p = PlayerComputer(i, 'computer', 'random')
    players_initial_order.append(p)
players_initial_order.append(PlayerComputer(4, 'computer', 'weighted_random'))
# players_initial_order.append(PlayerHuman(5, 'human'))

s0 = State(players_initial_order, 1, [], deck, {}, None)
winning_cards = {}
for i in range(0, 1000):
    simulate_episode(s0)
print('done')
