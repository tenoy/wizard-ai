import random
import threading
from collections import deque
from random import sample
from enum_rank import Rank
from enum_suit import Suit
from trick import Trick


class Simulation(threading.Thread):
    winning_cards = {}
    input_q = None
    output_q = None

    @staticmethod
    def simulate_episode(state, rollout_player=None, human_player=None):
        players_game_order = state.players
        max_number_of_rounds = int(60 / len(players_game_order))

        if rollout_player is None:
            deck = list(state.deck)
            number_of_rounds = max_number_of_rounds
        else:
            deck = [card for card in state.deck if card not in rollout_player.current_hand]
            number_of_rounds = state.round_nr

        for i in range(state.round_nr, min(number_of_rounds+1, max_number_of_rounds+1), 1):
            # create a new deque for 'in round order'
            players = deque(players_game_order)
            # determine number of cards to sample from deck
            if i == max_number_of_rounds:
                number_of_sampled_cards = i*len(players)
            else:
                # one additional card must be sampled for trump card
                number_of_sampled_cards = i*len(players)+1
            # reduce number of sampled card by the cards in hand of rollout player
            if state.round_nr == i and rollout_player is not None:
                number_of_sampled_cards = number_of_sampled_cards - len(rollout_player.current_hand)
            # Sample cards from deck
            sampled_cards = sample(deck, number_of_sampled_cards)

            # Each player gets their share of sampled cards
            start_idx = 0
            for player in players:
                if state.round_nr == i and rollout_player == player:
                    continue
                player.current_hand = sampled_cards[start_idx:start_idx+i]
                # player.current_hand = [deck[testing_card]]
                start_idx = start_idx + i
                # testing_card = testing_card + 1

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
            trump_card = None
            trump_suit = None
            if i < max_number_of_rounds:
                trump_card = sampled_cards[len(sampled_cards) - 1]
                if state.round_nr == i and rollout_player is not None:
                    trump_suit = state.trick.trump_suit
                else:
                    # trump_card = Card(Suit.JOKER, Rank.WIZARD) # for testing
                    trump_suit = trump_card.suit
                    if trump_suit == Suit.JOKER:
                        # if the dealer (i.e. player[0]) pulls a wizards as trump card, he might choose a trump suit
                        if trump_card.rank == Rank.WIZARD:
                            trump_suit = players[0].pick_suit(state)
                        else:
                            trump_suit = None
            state.trick.trump_suit = trump_suit

            if human_player is not None:
                Simulation.input_q.put('UPDATE_TRUMP')
                Simulation.input_q.join()

            # Place bids
            bids = {}
            state.bids = bids
            for player in players:
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
                    print('simulation: waiting')
                    Simulation.input_q.join()

            # Each player plays a card one after another in each trick j of round i
            for j in range(0, i, 1):
                trick = Trick(trump_suit=trump_suit, leading_suit=None, cards=[], played_by=[], trick_nr=j)
                state.trick = trick
                if human_player is not None:
                    Simulation.input_q.put('UPDATE_TRICK')
                    Simulation.input_q.join()
                    Simulation.input_q.put('UPDATE_STATS')
                    Simulation.input_q.join()
                for player in players:
                    played_card = player.play(trick, bids)
                    trick.add_card(played_card, player)
                    if trick.leading_suit is None:
                        trick.leading_suit = trick.get_leading_suit()
                    state.trick = trick
                    if human_player is not None:
                        Simulation.input_q.put('UPDATE_TRICK')
                        Simulation.input_q.join()
                        Simulation.input_q.put('UPDATE_STATS')
                        Simulation.input_q.join()
                highest_card = trick.get_highest_trick_card()
                win_count_card = Simulation.winning_cards.setdefault(highest_card, 0)
                Simulation.winning_cards[highest_card] = win_count_card + 1
                # evaluate trick winning player
                winning_player = None
                rotate_by = -1
                for k in range(0, len(players), 1):
                    player = players[k]
                    if player.played_cards[0] == highest_card:
                        player.current_tricks_won = player.current_tricks_won + 1
                        winning_player = player
                        rotate_by = len(players) - k
                for player in players:
                    if player.player_type == 'human':
                        print('Trump suit: ' + str(trump_suit))
                        print('Cards in trick: ', end=' ')
                        print(*trick.cards, sep=', ')
                        print('Winning card: ' + str(highest_card) + ' from ' + str(winning_player))
                        print('==============================================================')
                if human_player is not None:
                    Simulation.input_q.put('UPDATE_HAND')
                    Simulation.input_q.join()
                    Simulation.input_q.put('UPDATE_STATS')
                    Simulation.input_q.join()
                    Simulation.input_q.put('UPDATE_TRICK_WINNER')
                    Simulation.input_q.join()
                players.rotate(rotate_by)
                state.players = players
                if human_player is not None:
                    print(*players)
                    print(*state.players)


            # Calc score for each player and reset player hands etc
            for player in players_game_order:
                if player.current_bid == player.current_tricks_won:
                    player.current_score = player.current_score + 20 + player.current_tricks_won * 10
                else:
                    player.current_score = player.current_score - (abs(player.current_tricks_won - player.current_bid)) * 10
                # reset round dependent player vars
                player.current_tricks_won = 0
                player.current_bid = -1
                player.current_hand = []
                player.played_cards = deque()
                #print(str(player) + ', Score: ' + str(player.current_score))

            # next round another player starts
            players_game_order.rotate(1)
            state.players = players_game_order
            if rollout_player is None:
                state.round_nr = i + 1
                if 'human' in [player.player_type for player in players]:
                    print('Round ' + str(i) + ' done')
                    print('#############################################################')
            if human_player is not None:
                state.trick = Trick(trump_suit=trump_suit, leading_suit=None, cards=[], played_by=[])
                Simulation.input_q.put('UPDATE_TRICK')
                Simulation.input_q.join()

        # evaluate winning player
        highest_score = -10000000000
        highest_score_player = None
        player_final_scores = {}
        for player in players:
            player_final_scores[player] = player.current_score
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
            for player in state.players:
                print(str(player) + ', Games won: ' + str(player.games_won))
            if human_player is not None:
                Simulation.input_q.put('GAME_OVER')
                Simulation.input_q.join()

        if rollout_player is None:
            return player_final_scores
        else:
            return player_final_scores[rollout_player]
