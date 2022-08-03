from card import Card
from enum_rank import Rank
from enum_suit import Suit


def get_leading_suit(trick_cards):
    leading_suit = Suit.JOKER
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
    # case with trump in trick -> highest trump card wins
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
    if leading_suit != Suit.JOKER:
        leading_suit_cards = []
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

print('done')
