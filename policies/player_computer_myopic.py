import random
from enum_rank import Rank
from enum_suit import Suit
from policies.player_computer_weighted_random import PlayerComputerWeightedRandom


class PlayerComputerMyopic(PlayerComputerWeightedRandom):

    def calculate_bid(self, state):
        bid = 0
        for card in self.current_hand:
            if card.rank == Rank.WIZARD:
                bid = bid + 1
            else:
                prob = card.calc_static_win_prob(current_hand=self.current_hand, trump_card=state.trick.trump_card, players=state.players_deal_order)
                if prob >= 0.5:
                    bid = bid + 1
        return bid

    def select_card(self, state, legal_cards, played_cards=None):
        if self.current_tricks_won < self.current_bid:
            probs_dict = {}
            for card in legal_cards:
                probs_dict[card] = card.calc_dynamic_win_prob(trick=state.trick, cards_played=played_cards, current_hand=self.current_hand, cards_legal=legal_cards, players=state.players_play_order)
            prob_sum = 0
            for v in probs_dict.values():
                prob_sum = prob_sum + v
            if prob_sum == 0:
                probs_dict = self.build_static_probs_dict(cards=legal_cards, trump_card=state.trick.trump_card, players=state.players_play_order, win_prob=False)
        else:
            probs_dict = self.build_static_probs_dict(cards=legal_cards, trump_card=state.trick.trump_card, players=state.players_play_order, win_prob=False)
        max_prob = max(probs_dict.values())
        max_prob_cards = [card for card in probs_dict if probs_dict[card] == max_prob]
        # selected_card = max(probs_dict, key=probs_dict.get)
        # get the lowest rank card, that has maximum winning prob (i.e. win with the lowest card possible)
        min_max_card = self.get_min_max_card(max_prob_cards, state.trick)
        selected_card = min_max_card
        # selected_card = min(max_prob_cards)
        # print(f'Player_{self.number}, legal cards: {legal_cards}, probs: {probs_dict}, selected card: {selected_card}')
        return selected_card

    #trick, cards_played, cards_legal, current_hand, players
    def build_static_probs_dict(self, cards, trump_card, players, win_prob=True):
        probs_dict = {}
        for card in cards:
            prob = card.calc_static_win_prob(self.current_hand, trump_card, players)
            if not win_prob:
                prob = 1 - prob
            probs_dict[card] = prob
        return probs_dict

    def select_suit(self, state):
        suit_rank_sum_dict = {}
        for card in self.current_hand:
            if card.suit != Suit.JOKER:
                suit_rank_sum = suit_rank_sum_dict.setdefault(card.suit, 0)
                suit_rank_sum_dict[card.suit] = suit_rank_sum + card.rank
        if len(suit_rank_sum_dict) > 0:
            selected_suit = max(suit_rank_sum_dict, key=suit_rank_sum_dict.get)
        else:
            rnd_idx = random.randint(1, len(Suit) - 1)
            selected_suit = Suit(rnd_idx)
        return selected_suit

    @staticmethod
    def get_min_max_card(max_prob_cards, trick):
        min_max_card = max_prob_cards[0]
        for i in range(1, len(max_prob_cards)):
            card = max_prob_cards[i]
            # case if card has the same suit and possibly lower rank
            if card.suit == min_max_card.suit:
                if card.rank < min_max_card.rank:
                    min_max_card = card
            else:
                # case if min_max card has JOKER suit (either wizard for winning or jester for loosing) then rather take another card to save joker cards
                if min_max_card.suit == Suit.JOKER:
                    min_max_card = card
                # case if the min_max card is a trump card
                elif min_max_card.suit == trick.trump_suit:
                    # the other card must be non trump and non joker
                    if card.suit != trick.trump_suit and card.suit != Suit.JOKER:
                        min_max_card = card
                # case if the min_max card is a leading_suit card
                elif min_max_card.suit == trick.leading_suit:
                    # the other card must be non trump, non leading_suit and non joker (this case shouldnt happen...)
                    if card.suit != trick.trump_suit and card.suit != trick.leading_suit and card.suit != Suit.JOKER:
                        min_max_card = card
                # case if the min_max card is a normal card
                else:
                    # the other card must be non trump, non leading_suit and non joker
                    if card.suit != trick.trump_suit and card.suit != trick.leading_suit and card.suit != Suit.JOKER:
                        # and the rank must be lower
                        if card.rank < min_max_card.rank:
                            min_max_card = card

        return min_max_card
