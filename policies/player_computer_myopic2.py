from __future__ import annotations
from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_myopic import PlayerComputerMyopic
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state import State
    from card import Card


class PlayerComputerMyopic2(PlayerComputerMyopic):

    def calculate_bid(self, state: State) -> int:
        bid_cards = super().calculate_bid(state)
        sum_other_bids = sum(state.bids.values())
        # alpha is the weight on the sum of other bids -> "how munch to care about other bids"
        alpha = 0.1
        # adjust bid by taking other bids into account
        # if the sum of bids is lower than round number then increase bid, else decrease
        if bid_cards + sum_other_bids <= state.round_nr:
            bid = bid_cards + alpha * sum_other_bids
        else:
            bid = bid_cards - alpha * sum_other_bids
        bid = round(bid)
        # if bid != bid_cards:
        #     print("Changed bid")
        return bid

    def select_card(self, state: State, legal_cards: list[Card], played_cards: list[Card]=None) -> Card:
        if self.current_tricks_won < self.current_bid:
            probs_dict = {}
            prob_sum = 0
            last_ace_card = None
            for card in legal_cards:
                prob = card.calc_dynamic_win_prob(trick=state.trick, cards_played=played_cards, current_hand=self.current_hand, cards_legal=legal_cards, players=state.players_play_order)
                probs_dict[card] = prob
                prob_sum = prob_sum + prob
                # play ace as soon as possible and if not possible to definitely win with lower card
                if card.rank == Rank.ACE and card.suit != state.trick.trump_suit and prob > 0 and len(state.trick.cards) < len(state.players_play_order):
                    return card

            # no chance to win
            if prob_sum == 0:
                probs_dict = self.build_static_probs_dict(trick=state.trick, cards=legal_cards, players=state.players_play_order, win_prob=False)
                trash_cards = []
                max_prob = max(probs_dict.values())
                prob_interval = 0.1
                for card, prob in probs_dict.items():
                    # search for similarly bad prob cards and save jester
                    if prob + prob_interval > max_prob and card.rank != Rank.JESTER:
                        trash_cards.append(card)
                if len(trash_cards) == 1:
                    return trash_cards[0]
                elif len(trash_cards) > 1:
                    suits_dict = self.count_cards_per_suit(trash_cards)
                    most_common_suit = min(suits_dict, key=suits_dict.get)
                    trash_cards_most_common_suit = []
                    for card in trash_cards:
                        if card.suit == most_common_suit:
                            trash_cards_most_common_suit.append(card)

                    lowest_rank_most_common_trash_card = max(trash_cards_most_common_suit)
                    return lowest_rank_most_common_trash_card
        else:
            probs_dict = self.build_static_probs_dict(trick=state.trick, cards=legal_cards, players=state.players_play_order, win_prob=False)
        max_prob = max(probs_dict.values())
        max_prob_cards = [card for card in probs_dict if probs_dict[card] == max_prob]
        # selected_card = max(probs_dict, key=probs_dict.get)
        # get the lowest rank card, that has maximum winning prob (i.e. win with the lowest card possible)
        min_max_card = self.get_min_max_card(max_prob_cards, state.trick)
        selected_card = min_max_card
        # selected_card = min(max_prob_cards)
        # print(f'Player_{self.number}, legal cards: {legal_cards}, probs: {probs_dict}, selected card: {selected_card}')
        return selected_card

    @staticmethod
    def count_cards_per_suit(cards: list[Card]) -> dict[Card, int]:
        suit_card_count_dict = {}
        for card in cards:
            if suit_card_count_dict.get(card.suit) is not None:
                suit_card_count_dict[card.suit] = suit_card_count_dict[card.suit] + 1
            else:
                suit_card_count_dict[card.suit] = 1
        return suit_card_count_dict
