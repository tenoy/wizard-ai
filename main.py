from collections import deque
from random import sample

from card import Card
from enum_rank import Rank
from enum_suit import Suit
from player import Player


# Structure of game: Game -> Round -> Trick
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

trick1 = [deck[52], deck[54], deck[55], deck[56]]
#highest_card_trick1 = get_highest_card_in_trick(trick1, trump_suit=Suit.CLUBS)

trick2 = [deck[0], deck[1], deck[2], deck[55]]
#highest_card_trick2 = get_highest_card_in_trick(trick2, trump_suit=Suit.HEARTS)

# put in game class or something similar
number_of_players = 3
players = deque()
for i in range(1, number_of_players + 1, 1):
    p = Player(i, 'computer')
    players.append(p)
players.append(Player(4, 'human'))

number_of_rounds = int(60 / len(players))

for i in range(1, number_of_rounds, 1):
    # Sample cards from deck
    sampled_cards = sample(deck, i*len(players))
    # Sample trump suit (except in last round)
    trump_suit = None
    if i < number_of_rounds:
        trump_suit = sample(deck, 1)[0].suit
    # Each player gets their share of sampled cards and bid
    bids = []
    start_idx = 0
    for player in players:
        player.current_hand = sampled_cards[start_idx:start_idx+i]
        if player.player_type == 'computer':
            player.current_bid = player.make_bid(i, bids, players)
        else:
            print('Trump suit: ' + str(trump_suit))
            print('Current hand:')
            print(*player.current_hand)
            print('Previous bids:', end=' ')
            print(*bids)
            player.current_bid = input('Enter your bid: ')
            # todo check input bid
        bids.append(player.current_bid)
        start_idx = start_idx + i

    # Each player plays a card one after another in each trick
    for j in range(0, i, 1):
        trick = []
        leading_suit = None
        for player in players:
            if player.player_type == 'computer':
                played_card = player.play(trick, leading_suit)
            else:
                print('Trump suit: ' + str(trump_suit))
                print('Cards in trick:', end=' ')
                print(*trick)
                print('Current hand:')
                for k in range(0, len(player.current_hand)):
                    print('(' + str(k+1) + ') ' + str(player.current_hand[k]), end=' ')
                print('')
                idx = input('Select card: ')
                # todo: check selected card
                idx = int(idx) - 1
                player.played_card = player.current_hand[idx]

            trick.append(played_card)
            if leading_suit is None:
                leading_suit = get_leading_suit(trick)
        highest_card = get_highest_card_in_trick(trick, trump_suit, leading_suit)
        # evaluate trick winning player
        for player in players:
            if player.played_card == highest_card:
                player.current_tricks_won = player.current_tricks_won + 1
    # Calc score for each player and reset player hands etc
    for player in players:
        if player.current_bid == player.current_tricks_won:
            player.current_score = player.current_score + 20 + player.current_tricks_won * 10
        else:
            player.current_score = player.current_score - (abs(player.current_tricks_won - player.current_bid)) * 10
        player.current_tricks_won = 0
        player.current_bid = -1
        player.current_hand = []
        player.played_card = None
        print(player)
    # next round another player starts
    players.rotate(1)
    print(players)
    print('round done')
print('done')
