from __future__ import annotations
import random
import threading
from collections import deque
from random import sample
from enum_rank import Rank
from enum_suit import Suit
from trick import Trick
from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from state import State
    from player import Player


class Simulation(threading.Thread):
    winning_cards = {}
    input_q = None
    output_q = None

    @staticmethod
    def simulate_episode(state: State, rollout_player: Player=None, human_player: Player=None, game_nr: int=0, file_game: TextIO=None, file_round: TextIO=None, file_trick: TextIO=None) -> tuple[int, str] | dict[str, int]:
        players_deal_order = state.players_deal_order
        players_bid_order = state.players_bid_order
        players_play_order = state.players_play_order
        max_number_of_rounds = int(60 / len(players_deal_order))
        # the number of rounds is different for rollout simulation instances
        if rollout_player is None:
            deck = list(state.deck)
            number_of_rounds = max_number_of_rounds
        else:
            deck = [card for card in state.deck if card not in rollout_player.current_hand and card not in state.played_cards]
            if state.trick.trump_card is not None:
                deck.remove(state.trick.trump_card)
            number_of_rounds = state.round_nr

        # simulate rounds from round_nr to min of number of rounds or max number of rounds
        for i in range(state.round_nr, min(number_of_rounds+1, max_number_of_rounds+1), 1):
            # determine number of cards to sample from deck
            if i == max_number_of_rounds:
                number_of_sampled_cards = i*len(players_deal_order)
            else:
                # one additional card must be sampled for trump card
                number_of_sampled_cards = i*len(players_deal_order)+1
            # reduce number of sampled card by the cards in hand of rollout player
            if state.round_nr == i and rollout_player is not None:
                number_of_sampled_cards = number_of_sampled_cards - len(rollout_player.current_hand) - len(state.played_cards)
            # Sample cards from deck
            sampled_cards = sample(deck, number_of_sampled_cards)

            # Each player gets their share of sampled cards
            player_cards_dict = {}
            for player in players_deal_order:
                if rollout_player is not None:
                    player_cards_dict[player] = len(player.current_hand)
                else:
                    player_cards_dict[player] = i

            start_idx = 0
            for player in players_deal_order:
                if state.round_nr == i and rollout_player == player:
                    continue
                player.current_hand = sampled_cards[start_idx:start_idx+player_cards_dict[player]]
                start_idx = start_idx + player_cards_dict[player]

            if human_player is not None:
                Simulation.input_q.put('UPDATE_ROUND')
                Simulation.input_q.join()
                Simulation.input_q.put('UPDATE_STATS')
                Simulation.input_q.join()
                Simulation.input_q.put('UPDATE_HAND')
                Simulation.input_q.join()
                # Simulation.q.put('UPDATE_TRUMP')
                # Simulation.q.join()
                Simulation.input_q.put('UPDATE_TRICK')
                Simulation.input_q.join()

            # Sample trump suit (except in last round)
            trump_suit = None
            trump_card = None
            # players[0].pick_suit(state)
            if i < max_number_of_rounds:
                if state.round_nr == i and rollout_player is not None:
                    trump_card = state.trick.trump_card
                    trump_suit = state.trick.trump_suit
                else:
                    trump_card = sampled_cards[len(sampled_cards) - 1]
                    trump_suit = trump_card.suit
                    if trump_suit == Suit.JOKER:
                        # if the dealer (i.e. player[0]) pulls a wizards as trump card, he might choose a trump suit
                        if trump_card.rank == Rank.WIZARD:
                            # players_deal_order[0] is the dealer - if a wizard is drawn as trump, he may choose a suit
                            trump_suit = players_deal_order[0].pick_suit(state)
                        else:
                            trump_suit = None
            state.trick.trump_card = trump_card
            state.trick.trump_suit = trump_suit

            # Place bids - the player after the dealer starts with bidding

            if human_player is not None:
                Simulation.input_q.put('UPDATE_TRUMP')
                Simulation.input_q.join()
                Simulation.input_q.put('UPDATE_STATS')
                # print('simulation: waiting')
                # print(f'simulation: {Simulation.input_q.queue}')
                Simulation.input_q.join()

            bids = {}
            state.bids = bids
            for player in players_bid_order:
                if state.round_nr == i and rollout_player == player:
                    player.current_bid = rollout_player.current_bid
                    # it might be that a valid bid in starting state is not valid in rollout state
                    if not rollout_player.is_valid_bid(state, rollout_player.current_bid):
                        player.current_bid = rollout_player.recalculate_bid(state, rollout_player.current_bid)
                else:
                    player.current_bid = player.make_bid(state)
                bids[player] = player.current_bid
                state.bids = bids
                if human_player is not None:
                    Simulation.input_q.put('UPDATE_STATS')
                    # print('simulation: waiting')
                    # print(f'simulation: {Simulation.input_q.queue}')
                    Simulation.input_q.join()
                    Simulation.input_q.put('UPDATE_TRICK')
                    # print('simulation: waiting')
                    # print(f'simulation: {Simulation.input_q.queue}')
                    Simulation.input_q.join()

            # in a rollout simulation run, the round nr and trick nr needs to be stored before state.trick is changed in trick loop
            if rollout_player is not None:
                rollout_round = state.trick.round_nr
                rollout_trick_nr = state.trick.trick_nr
            else:
                rollout_round = -1
                rollout_trick_nr = -1

            # The player after the next player of the dealer starts the play
            # Each player plays a card one after another in each trick j of round i
            for j in range(state.trick.trick_nr, i+1):
                if rollout_player is not None:
                    if rollout_player.policy == 'myopic_rollout_play' and i == rollout_round and j == rollout_trick_nr:
                        trick = state.trick
                    else:
                        trick = Trick(trump_card=trump_card, trump_suit=trump_suit, leading_suit=None, cards=[], played_by=[], round_nr=i, trick_nr=j)
                else:
                    trick = Trick(trump_card=trump_card, trump_suit=trump_suit, leading_suit=None, cards=[], played_by=[], round_nr=i, trick_nr=j)
                state.trick = trick

                # gui update for a human player
                if human_player is not None:
                    Simulation.input_q.put('UPDATE_TRICK')
                    Simulation.input_q.join()
                    Simulation.input_q.put('UPDATE_STATS')
                    Simulation.input_q.join()

                for player in players_play_order:
                    # skip players that already have played a card (happens in rollout instances)
                    if player in trick.played_by:
                        continue
                    if state.round_nr == i and rollout_player == player:
                        if player.policy == 'myopic_rollout_play' and i == rollout_round and j == rollout_trick_nr:
                            played_card = rollout_player.current_hand[rollout_player.current_card_idx]
                            rollout_player.played_cards.appendleft(played_card)
                            rollout_player.current_hand.remove(played_card)
                        else:
                            played_card = player.play(state)
                    else:
                        played_card = player.play(state)

                    trick.add_card(played_card, player)
                    state.played_cards.append(played_card)

                    if trick.leading_suit is None:
                        trick.leading_suit = trick.get_leading_suit()
                    state.trick = trick

                    # gui update for a human player
                    if human_player is not None:
                        Simulation.input_q.put('UPDATE_TRICK')
                        Simulation.input_q.join()
                        Simulation.input_q.put('UPDATE_STATS')
                        Simulation.input_q.join()

                # get winning card
                highest_card_idx = trick.get_highest_trick_card_index()
                highest_card = trick.cards[highest_card_idx]
                win_count_card = Simulation.winning_cards.setdefault(highest_card, 0)
                Simulation.winning_cards[highest_card] = win_count_card + 1
                # update winning player
                winning_player = players_play_order[highest_card_idx]
                winning_player.current_tricks_won = winning_player.current_tricks_won + 1
                # rotate players_play_order such that winning player plays first in next trick
                rotate_by = len(players_play_order) - highest_card_idx
                # write to csv
                if file_trick is not None:
                    for player_pos in range(0, len(players_play_order)):
                        player = players_play_order[player_pos]
                        file_trick.write(str(game_nr) + ',' + str(i) + ',' + str(trick.trump_card) + ',' + str(trick.trump_suit) + ',' + str(j) + ',' + str(trick.leading_suit) + ',' + str(highest_card) + ',' + str(player) + ',' + str(player_pos) + ',' + str(trick.cards[player_pos]) + '\n')

                # console output for a human player
                for player in players_play_order:
                    if player.player_type == 'human':
                        print('Trump card: ' + str(trump_card))
                        print('Trump suit: ' + str(trump_suit))
                        print('Cards in trick: ', end=' ')
                        print(*trick.cards, sep=', ')
                        print('Winning card: ' + str(highest_card) + ' from ' + str(winning_player))
                        print('==============================================================')
                # gui update for a human player
                if human_player is not None:
                    Simulation.input_q.put('UPDATE_HAND')
                    Simulation.input_q.join()
                    Simulation.input_q.put('UPDATE_STATS')
                    Simulation.input_q.join()
                    Simulation.input_q.put('UPDATE_TRICK_WINNER')
                    Simulation.input_q.join()

                players_play_order.rotate(rotate_by)
                state.players_play_order = players_play_order
                state.tricks.append(trick)
                # trick = Trick(trump_suit=None, leading_suit=None, cards=[], played_by=[])
                if human_player is not None:
                    print(*players_play_order)
                    print(*state.players_deal_order)

            # Calc score for each player and reset player hands etc
            for player_pos in range(0, len(players_bid_order)):
                player = players_deal_order[player_pos]
                if player.current_bid == player.current_tricks_won:
                    player.current_score = player.current_score + 20 + player.current_tricks_won * 10
                else:
                    player.current_score = player.current_score - (abs(player.current_tricks_won - player.current_bid)) * 10

                if file_round is not None:
                    file_round.write(str(game_nr) + ',' + str(i) + ',' + str(trick.trump_card) + ',' + str(trick.trump_suit) + ',' + str(player) + ',' + str(player_pos) + ',' + str(player.current_bid) + ',' + str(player.current_tricks_won) + ',' + str(player.current_score) + '\n')
                # reset round dependent player vars
                player.current_tricks_won = 0
                player.current_bid = -1
                player.current_hand = []
                player.played_cards = deque()
                #print(str(player) + ', Score: ' + str(player.current_score))
            # if human_player is not None:
            #     Simulation.input_q.put('GAME_OVER')
            #     Simulation.input_q.join()

            # next round another player starts
            players_deal_order.rotate(-1)
            players_bid_order.rotate(-1)
            players_play_order = deque(players_deal_order)
            state.players_play_order = players_play_order
            players_play_order.rotate(-2)
            trick = Trick(trump_suit=None, leading_suit=None, cards=[], played_by=[], trick_nr=1)
            state.trick = trick
            state.played_cards = []

            if rollout_player is None:
                state.round_nr = i + 1
                if 'human' in [player.player_type for player in players_deal_order]:
                    print('Round ' + str(i) + ' done')
                    print('#############################################################')
            if human_player is not None:
                # state.trick = Trick(trump_suit=trump_suit, leading_suit=None, cards=[], played_by=[])
                Simulation.input_q.put('UPDATE_TRICK')
                Simulation.input_q.join()

        if human_player is not None:
            Simulation.input_q.put('UPDATE_STATS')
            Simulation.input_q.join()
            Simulation.input_q.put('GAME_OVER')
            Simulation.input_q.join()

        # evaluate winning player
        highest_score = -10000000000
        highest_score_player = None
        player_final_scores = {}
        for player in players_deal_order:
            # write game score
            if file_game is not None:
                file_game.write(str(game_nr) + ',' + str(player) + ',' + str(player_pos) + ',' + str(player.current_score) + '\n')
            # get highest score player
            player_final_scores[str(player)] = player.current_score
            if player.current_score > highest_score:
                highest_score = player.current_score
                highest_score_player = player
            elif player.current_score == highest_score:
                rnd = random.randint(0, 1)
                if rnd == 0:
                    highest_score = player.current_score
                    highest_score_player = player
            player.current_score = 0
        if rollout_player is None:
            highest_score_player.games_won = highest_score_player.games_won + 1
            # for player in state.players_deal_order:
                # print(str(player) + ', Games won: ' + str(player.games_won))

        if rollout_player is None:
            # print(f'Game {} done')
            return player_final_scores, str(highest_score_player)
        else:
            return player_final_scores[str(rollout_player)]
