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
        players_deal_order = state.players_deal_order
        players_bid_order = state.players_bid_order
        players_play_order = state.players_play_order
        max_number_of_rounds = int(60 / len(players_deal_order))
        # the number of rounds is different for rollout simulation instances
        if rollout_player is None:
            deck = list(state.deck)
            number_of_rounds = max_number_of_rounds
            # in a normal state the order of players need to be set for each list
            players_bid_order.rotate(-1)
            players_play_order.rotate(-2)
        else:
            deck = [card for card in state.deck if card not in rollout_player.current_hand]
            if state.trick.trump_card is not None:
                deck.remove(state.trick.trump_card)
            number_of_rounds = state.round_nr

        # simulate rounds from round_nr to min of number of rounds or max number of rounds
        for i in range(state.round_nr, min(number_of_rounds+1, max_number_of_rounds+1), 1):
            # create a new deque for 'in round order'
            # players = deque(players_deal_order)
            # determine number of cards to sample from deck
            if i == max_number_of_rounds:
                number_of_sampled_cards = i*len(players_deal_order)
            else:
                # one additional card must be sampled for trump card
                number_of_sampled_cards = i*len(players_deal_order)+1
            # reduce number of sampled card by the cards in hand of rollout player
            if state.round_nr == i and rollout_player is not None:
                number_of_sampled_cards = number_of_sampled_cards - len(rollout_player.current_hand)
            # Sample cards from deck
            sampled_cards = sample(deck, number_of_sampled_cards)

            # Each player gets their share of sampled cards
            start_idx = 0
            for player in players_deal_order:
                if state.round_nr == i and rollout_player == player:
                    continue
                player.current_hand = sampled_cards[start_idx:start_idx+i]
                start_idx = start_idx + i

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

            # The player after the next player of the dealer starts the play
            # Each player plays a card one after another in each trick j of round i
            for j in range(0, i, 1):
                trick = Trick(trump_card=trump_card, trump_suit=trump_suit, leading_suit=None, cards=[], played_by=[], round_nr=i, trick_nr=j)
                state.trick = trick
                if human_player is not None:
                    Simulation.input_q.put('UPDATE_TRICK')
                    Simulation.input_q.join()
                    Simulation.input_q.put('UPDATE_STATS')
                    Simulation.input_q.join()
                for player in players_play_order:
                    played_card = player.play(state)
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
                for k in range(0, len(players_play_order), 1):
                    player = players_play_order[k]
                    if player.played_cards[0] == highest_card:
                        player.current_tricks_won = player.current_tricks_won + 1
                        winning_player = player
                        # determine the number for queue rotation so that winning player starts in next trick
                        rotate_by = len(players_play_order) - k
                for player in players_play_order:
                    if player.player_type == 'human':
                        print('Trump card: ' + str(trump_card))
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
                players_play_order.rotate(rotate_by)
                state.players_play_order = players_play_order
                if human_player is not None:
                    print(*players_play_order)
                    print(*state.players_deal_order)


            # Calc score for each player and reset player hands etc
            for player in players_deal_order:
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
            # if human_player is not None:
            #     Simulation.input_q.put('GAME_OVER')
            #     Simulation.input_q.join()

            # next round another player starts
            players_deal_order.rotate(-1)
            players_bid_order.rotate(-1)
            players_play_order = deque(players_deal_order)
            state.players_play_order = players_play_order
            players_play_order.rotate(-2)
            trick = Trick(trump_suit=None, leading_suit=None, cards=[], played_by=[])
            state.trick = Trick(trump_suit=None, leading_suit=None, cards=[], played_by=[])

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
