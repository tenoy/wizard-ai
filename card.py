from abc import ABC, abstractmethod


class Card:
    def __init__(self, suit, rank):
        self.color = suit
        self.rank = rank

    @abstractmethod
    def __gt__(self, other_card, leading_suit, trump_suit):
        pass




