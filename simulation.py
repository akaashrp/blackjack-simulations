import random
import re
import numpy as np
from numpy.linalg import matrix_power
import seaborn as sns
import matplotlib.pyplot as plt
import math

global card_names
cards = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}
global suits
suits = {0: "H", 1: "D", 2: "S", 3: "C"}

class Card:
    def __init__(self, value: int, card: str, suit: int, deck: int):
        self.value = value
        self.card = card
        self.suit = suit
        self.deck = deck

    def set_value(self, value): # for aces
        self.value = value

    def is_ace(self):
        return self.card == "A"

    def __str__(self):
        return f"{self.value}, ({self.card}, {suits[self.suit]}), {self.deck}"

class Deck:
    def __init__(self, size):
        self.cards = []
        count = 0
        deck = 1
        while count < size:
            for suit in suits.keys():
                for card_name in cards.keys():
                    if count > size:
                        break
                    card = Card(cards[card_name], card_name, suit, deck)
                    self.cards.append(card)
                    count += 1
            deck += 1
        random.shuffle(self.cards)
    
    def draw(self):
        if len(self.cards) == 0:
            return None
        card = self.cards[0]
        self.cards.pop(0)
        return card
    
    def remove_card(self, card):
        self.cards.remove(card)
    
    def __str__(self):
        return f"{[str(i) for i in self.cards]}"

class Hand:
    def __init__(self, cards: list):
        self.cards = cards
    
    def add_card(self, card):
        self.cards.append(card)
    
    def count_aces(self):
        return len([i for i in self.cards if i.card == "A"])
    
    def get_points(self):
        points = 0
        for card in self.cards:
            if card.card == "A":
                continue
            points += card.value
        for i in range(self.count_aces()):
            if points >= 11:
                points += 1
            else:
                points += 11

        return points
    
    def __str__(self):
        return f"{[str(i) for i in self.cards]}"

class Player:
    def __init__(self, hand):
        self.hand = hand
    
class Dealer:
    def __init__(self, hand):
        self.hand = hand

def initial_deal(deck):
    pc1 = deck.draw()
    dc1 = deck.draw()
    pc2 = deck.draw()
    dc2 = deck.draw()
    player_hand = Hand([pc1, pc2])
    dealer_hand = Hand([dc1, dc2])
    return player_hand, dealer_hand

def player_strategy1(player_hand, dealer_hand, deck):
    if player_hand.get_points() == 21 and dealer_hand.get_points() != 21:
        return "natural"
    elif dealer_hand.get_points() == 21 and player_hand.get_points() != 21:
        return "dealer"
    elif dealer_hand.get_points() == 21 and player_hand.get_points() == 21:
        return "tie"
    while (player_hand.get_points() < 17):
        player_hand.add_card(deck.draw())
    if player_hand.get_points() > 21:
        return "dealer"
    while (dealer_hand.get_points() < 17):
        dealer_hand.add_card(deck.draw())
    if dealer_hand.get_points() > 21:
        return "player"
    if player_hand.get_points() > dealer_hand.get_points():
        return "player"
    elif player_hand.get_points() < dealer_hand.get_points():
        return "dealer"
    return "tie"

def is_busted(hand, deck):
    while (hand.get_points() < 17):
        hand.add_card(deck.draw())
    return hand.get_points(), hand.get_points() > 21

def simulate_dealer_bust():
    num_simulations = 500000
    results = {17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, -1: 0}
    for i in range(num_simulations):
        deck = Deck(52)
        dealer_hand = Hand([deck.draw()])
        #player_hand, dealer_hand = initial_deal(deck)
        points, busted = is_busted(dealer_hand, deck)
        if len(dealer_hand.cards) == 2 and dealer_hand.get_points() == 21: # natural blackjack
            results[22] += 1
        elif busted:
            results[-1] += 1
        else:
            results[points] += 1
    
    normalized_results = {k: v / num_simulations for k, v in results.items()}
    return normalized_results

def simulate_dealer_results_upcard():
    num_simulations = 500000
    results = {k: {17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, -1: 0} for k in cards.keys()}
    for i in range(num_simulations):
        deck = Deck(52)
        initial_card = deck.draw()
        dealer_hand = Hand([initial_card])
        #player_hand, dealer_hand = initial_deal(deck)
        points, busted = is_busted(dealer_hand, deck)

        if len(dealer_hand.cards) == 2 and dealer_hand.get_points() == 21: # natural blackjack
            results[initial_card.card][22] += 1
        elif busted:
            results[initial_card.card][-1] += 1
        else:
            results[initial_card.card][points] += 1
    
    normalized_results = {k: {k2: v2 / sum(v.values()) for k2, v2 in v.items()} for k, v in results.items()}
    return normalized_results

def simulate_ps1():
    num_simulations = 500000
    results = {"player": 0, "dealer": 0, "tie": 0, "natural": 0}
    for i in range(num_simulations):
        deck = Deck(104)
        player_hand, dealer_hand = initial_deal(deck)
        result = player_strategy1(player_hand, dealer_hand, deck)
        results[result] += 1
    
    normalized_results = {k: v / num_simulations for k, v in results.items()}
    expectation = normalized_results["player"] * 1 + normalized_results["dealer"] * -1 + normalized_results["blackjack"] * 1.5
    return normalized_results, expectation
    
def markov_process():
    def get_probabilities():
        probabilities = {cards[i]: 1 / 13 for i in cards.keys()}
        probabilities[10] = 4 / 13
        probabilities[1] = 1 / 13
        return probabilities
    
    def get_state_space():
        # state space
        first = [str(i) + "f" for i in range(2, 12)]
        hard = [str(i) + "h" for i in range(4, 17)]
        soft = [str(i) + "s" for i in range(12, 17)]
        stand = [str(i) + "d" for i in range(17, 22)]
        bj = ["bj"]
        bust = ["bust"]
        states = first + hard + soft + stand + bj + bust
        num_states = len(states)
        return states, num_states

    states, num_states = get_state_space()
    start = list(range(10))
    end = list(range(num_states - 7, num_states))
    probabilities = get_probabilities()

    def construct_transition_matrix():
        # let P[i][j] be the one-step transition probability from i to j
        P = {i: {j: 0 for j in states} for i in states}
        for i in states:
            for j in states:
                if i[-1] == "f": # first
                    if j[-1] == "h": # hard
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        diff = j_val - i_val
                        if i_val <= 10 and j_val <= 16 and 2 <= diff <= 10:
                            P[i][j] += probabilities.get(diff, 0)
                    
                    elif j[-1] == "s": # soft - dealer stands on soft 17
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        diff = j_val - i_val
                        if i_val == 11 and j_val > i_val and j_val <= 16:
                            P[i][j] += probabilities.get(diff, 0)
                        elif 2 <= i_val <= 5 and diff == 11:
                            P[i][j] += probabilities.get(11, 0)
                    
                    elif j[-1] == "d": # stand
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        diff = j_val - i_val
                        if 17 <= j_val <= 20:
                            P[i][j] += probabilities.get(diff, 0)
                    
                    elif j == "bj": # blackjack
                        if i == "10f":
                            P[i][j] += probabilities.get(11, 0)
                        elif i == "11f":
                            P[i][j] += probabilities.get(10, 0)

                elif i[-1] == "h":
                    if j[-1] == "h":
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        diff = j_val - i_val
                        if i_val >= 11 and j_val <= 16 and diff == 1:
                            P[i][j] += probabilities.get(1, 0)
                        if 2 <= diff <= 10 and j_val <= 16:
                            P[i][j] += probabilities.get(diff, 0)

                    elif j[-1] == "s": # h to s is only possible for 4h (A + 4), 5h (A + 5)
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        diff = j_val - i_val
                        if (i_val == 4 or i_val == 5) and diff == 11:
                            P[i][j] += probabilities.get(11, 0)
                        
                    elif j[-1] == "d": # h to d
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        diff = j_val - i_val
                        if 17 <= j_val <= 21 and diff <= 11:
                            P[i][j] += probabilities.get(diff, 0)
                        
                    elif j == "bust":
                        i_val = int(extract_digits(i)[0])
                        diff = 22 - i_val
                        if diff >= 11:
                            continue
                        for k in range(diff, 11):
                            P[i][j] += probabilities.get(k, 0)
                
                elif i[-1] == "s": # s: 12s, 13s, 14s, 15s, 16s
                    if j[-1] == "s":
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        diff = j_val - i_val
                        if 12 <= i_val <= 15 and j_val > i_val and j_val <= 16:
                            P[i][j] += probabilities.get(diff, 0)

                    elif j[-1] == "h": # s to h
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        if j_val >= i_val:
                            continue
                        diff = j_val + 11 - i_val
                        if i_val == 12 and diff == 10:
                            P[i][j] += probabilities.get(diff, 0)
                        elif i_val == 13 and 9 <= diff <= 10:
                            P[i][j] += probabilities.get(diff, 0)
                        elif i_val == 14 and 8 <= diff <= 10:
                            P[i][j] += probabilities.get(diff, 0)
                        elif i_val == 15 and 7 <= diff <= 10:
                            P[i][j] += probabilities.get(diff, 0)
                        elif i_val == 16 and 6 <= diff <= 10:
                            P[i][j] += probabilities.get(diff, 0)

                    elif j[-1] == "d":
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        diff = j_val - i_val
                        if 17 <= j_val <= 21 and 2 <= diff <= 11:
                            P[i][j] += probabilities.get(diff, 0)
                        if i_val == 16 and diff == 1:
                            P[i][j] += probabilities.get(1, 0)

                elif i[-1] == "d":
                    if j[-1] == "d":
                        i_val = int(extract_digits(i)[0])
                        j_val = int(extract_digits(j)[0])
                        if i_val == j_val:
                            P[i][j] = 1
                
                elif i == "bj":
                    if j == "bj":
                        P[i][j] = 1

                elif i == "bust":
                    if j == "bust":
                        P[i][j] = 1
        
        P = [[P[i][j] for j in states] for i in states]
        P = np.array(P)
        P = matrix_power(P, 17) # P^17 (at most 17 transitions)
        return P

    P = construct_transition_matrix()
    P = [[P[i][j] for j in end] for i in start]
    for i in range(len(P)):
        assert(math.isclose(sum(P[i]), 1, abs_tol=1e-5))
    
    return P

def extract_digits(s):
    return re.findall(r'\d+', s)

def get_player_stay_expectations(transition_matrix):
    player_stay_expectations = [[0 for j in range(len(transition_matrix[0]))] for i in range(len(transition_matrix))] # <=16, 17, 18, 19, 20, 21, BJ

    for i in range(len(transition_matrix)):
        row_sum = sum(transition_matrix[i])
        vals = [transition_matrix[i][-1]] + [transition_matrix[i][j] for j in range(len(transition_matrix[i]) - 1)]
        for j in range(1, len(vals) - 1):
            player_stay_expectations[i][j] = 1 * sum(vals[0:j]) + (-1) * (row_sum - sum(vals[0:j+1]))

        player_stay_expectations[i][0] = 1 * transition_matrix[i][-1] + (-1) * (row_sum - transition_matrix[i][-1]) # <= 16
        player_stay_expectations[i][6] = 1.5 * (row_sum - transition_matrix[i][-2])
    
    player_stay_expectations = np.array(player_stay_expectations)
    return player_stay_expectations

def get_player_draw_expectations(transition_matrix):
    dealer_upcards = [i for i in range(2, 12)]
    player_totals = [i for i in range(11, 20)]
    player_draw_expectations = [[0 for j in range(len(player_totals))] for i in range(len(dealer_upcards))] # <=16, 17, 18, 19, 20, 21, BJ
    for card in dealer_upcards:
        for total in player_totals:
            for i in range(10000):
                deck = Deck(52)
                player_points = deck.draw().value + total
                dealer_hand = Hand([Card(card, str(card), 0, 1)])
                while (dealer_hand.get_points() < 17):
                    dealer_hand.add_card(deck.draw())

                if player_points > 21:
                    player_draw_expectations[card - 2][total - 11] += -1
                elif dealer_hand.get_points() > 21:
                    player_draw_expectations[card - 2][total - 11] += 1
                elif player_points > dealer_hand.get_points():
                    player_draw_expectations[card - 2][total - 11] += 1
                elif player_points < dealer_hand.get_points():
                    player_draw_expectations[card - 2][total - 11] += -1

            player_draw_expectations[card - 2][total - 11] /= 10000

    player_draw_expectations = np.array(player_draw_expectations)
    return player_draw_expectations

def generate_dealer_upcard_heatmap():
    transition_matrix = markov_process() # rows represent dealer up-card, columns represent final total

    ylabels = list(range(2, 12))
    xlabels = list(range(17, 22)) + ["bj", "bust"]

    heatmap = sns.heatmap(transition_matrix, annot=True, fmt=".5f", cmap="Blues")
    heatmap.set(xlabel = "dealer final total", ylabel = "dealer upcard")
    plt.xticks(np.arange(7), xlabels)
    plt.yticks(np.arange(10), ylabels)
    plt.show()

def generate_player_stay_expectations_heatmap():
    transition_matrix = markov_process() # rows represent dealer up-card, columns represent final total

    player_stay_expectations = get_player_stay_expectations(transition_matrix)

    ylabels = list(range(2, 12))
    xlabels = ["<=16"] + list(range(17, 22)) + ["bj"]

    heatmap = sns.heatmap(player_stay_expectations, annot=True, fmt=".5f", cmap="Blues")
    heatmap.set(xlabel = "player total", ylabel = "dealer upcard")
    plt.xticks(np.arange(7), xlabels)
    plt.yticks(np.arange(10), ylabels)
    plt.show()
