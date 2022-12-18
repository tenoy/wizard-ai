from enum_rank import Rank
from enum_suit import Suit


def contains_current_hand_leading_suit(current_hand, leading_suit):
    for card in current_hand:
        if card.suit == leading_suit:
            return True
    return False


def get_legal_cards(current_hand, leading_suit):
    # prepare set of cards that are allowed to play so that the policies dont have to deal with that again and again
    legal_cards = []
    if leading_suit is None or leading_suit == Suit.JOKER or not has_leading_suit_in_hand(leading_suit):
        legal_cards.extend(current_hand)
    else:
        for card in current_hand:
            if card.suit == leading_suit or card.suit == Suit.JOKER:
                legal_cards.append(card)
    return legal_cards


def get_highest_legal_card(legal_cards, trump_suit, leading_suit):
    # case with empty legal cards
    if len(legal_cards) == 0:
        return None

    # case with wizard in legal cards
    for card in legal_cards:
        if card.rank == Rank.WIZARD:
            return card

    # case with trump in legal cards -> get highest trump card
    if trump_suit is not None:
        trump_cards = []
        for card in legal_cards:
            if card.suit == trump_suit:
                trump_cards.append(card)

        if len(trump_cards) == 1:
            return trump_cards[0]
        elif len(trump_cards) > 1:
            return max(trump_cards)

    # case without wizard or trump card
    leading_suit_cards = []
    if leading_suit is not None and leading_suit != Suit.JOKER:
        for card in legal_cards:
            if card.suit == leading_suit:
                leading_suit_cards.append(card)

        if len(leading_suit_cards) == 1:
            return leading_suit_cards[0]
        elif len(leading_suit_cards) > 1:
            return max(leading_suit_cards)
        else:
            return max(legal_cards)
    else:
        # case where no leading suit is in trick or leading suit is a joker card
        return max(legal_cards)


def get_played_cards(players):
    played_cards = list()
    for player in players:
        played_cards.extend(player.played_cards)
    return played_cards
