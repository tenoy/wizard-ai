from random import sample

from card import Card
from enum_rank import Rank
from enum_suit import Suit
from player import Player


# Structure of game: Game -> Round -> Trick
def get_leading_suit(trick_cards):
    leading_suit = None
    for card in trick_cards:
        if card.suit != Suit.JOKER:
            leading_suit = card.suit
            return leading_suit
    return leading_suit


def get_highest_card_in_trick(trick_cards, trump_suit):
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
        else:
            return max(trump_cards)

    # case without wizard or trump card
    leading_suit = get_leading_suit(trick_cards)
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
        print(c)

for i in range(1, 5, 1):
    c = Card(Suit.JOKER, Rank.JESTER)
    deck.append(c)
    print(c)

for i in range(1, 5, 1):
    c = Card(Suit.JOKER, Rank.WIZARD)
    deck.append(c)
    print(c)

trick1 = [deck[52], deck[54], deck[55], deck[56]]
highest_card_trick1 = get_highest_card_in_trick(trick1, trump_suit=Suit.CLUBS)

trick2 = [deck[0], deck[1], deck[2], deck[55]]
highest_card_trick2 = get_highest_card_in_trick(trick2, trump_suit=Suit.HEARTS)

# put in game class or something similar
number_of_players = 3
players = []
for i in range(1, number_of_players + 1, 1):
    p = Player(i)

number_of_rounds = int(60 / number_of_players)

for i in range(1, number_of_rounds, 1):
    # Sample i times number of player cards
    sampled_cards = sample(deck, i*number_of_players)
    # Sample trump suit except in last round
    trump_suit = None
    if i < number_of_rounds:
        trump_suit = sample(deck, 1)[0].suit
    for player in players:
        for j in range(1, i + 1, 1):
            print('bla')

print('done')
