from card import Card
from enum_rank import Rank
from enum_suit import Suit


deck = []
for i in range(1, 5, 1):
    for j in range(2, 15, 1):
        c = Card(Suit(i), Rank(j))
        deck.append(c)
        print(c)

for i in range(1, 5, 1):
    c = Card(Suit(5), Rank(1))
    deck.append(c)
    print(c)

for i in range(1, 5, 1):
    c = Card(Suit(5), Rank(15))
    deck.append(c)
    print(c)



print('done')
