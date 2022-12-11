from enum_rank import Rank
from enum_suit import Suit


def get_played_cards(players):
    played_cards = list()
    for player in players:
        played_cards.extend(player.played_cards)
    return played_cards

