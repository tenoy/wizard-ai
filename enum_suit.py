from enum import Enum


@Enum.unique
class Suit(Enum):
    HEARTS = 1
    CLUBS = 2       #Kreuz
    SPADES = 3      #Pik
    DIAMONDS = 4    #Karo
