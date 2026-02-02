from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from deuces import Card, Evaluator
import random
import traceback
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

evaluator = Evaluator()

# --- Card Conversion & Deck Logic ---
def to_deuces_card(card_str):
    rank = card_str[0].upper()
    suit = card_str[1].lower()
    return Card.new(rank + suit)

def create_deck():
    return [Card.new(r + s) for r in '23456789TJQKA' for s in 'shdc']

# --- Pre-flop Analysis (Chen Formula) ---
def get_chen_score(hand):
    score = 0
    ranks = sorted([Card.get_rank_int(c) for c in hand], reverse=True)
    rank_map = {12: 10, 11: 8, 10: 7, 9: 6, 8: 5} # A, K, Q, J, T
    high_card_rank = ranks[0]
    
    score = rank_map.get(high_card_rank, high_card_rank + 2)
    
    is_pair = ranks[0] == ranks[1]
    if is_pair:
        score = max(5, score * 2)

    if Card.get_suit_int(hand[0]) == Card.get_suit_int(hand[1]):
        score += 2
        
    gap = ranks[0] - ranks[1]
    if gap > 0 and gap < 5 and not is_pair:
        gap_penalties = {1: 0, 2: -1, 3: -2, 4: -4}
        score += gap_penalties.get(gap, -5)
    elif not is_pair:
        score -= 5

    if not is_pair and gap < 3 and high_card_rank < 10: # Q
        score += 1
        
    return round(score)

# --- Monte Carlo Simulation ---
def run_monte_carlo(my_hand_deuces, board_deuces, num_opponents, simulations=1000):
    wins = 0
    deck = create_deck()
    
    known_cards = my_hand_deuces + board_deuces
    for card in known_cards:
        if card in deck: deck.remove(card)

    for _ in range(simulations):
        shuffled_deck = list(deck)
        random.shuffle(shuffled_deck)
        
        opponent_hands = [shuffled_deck[i*2:i*2+2] for i in range(num_opponents)]
        
        board_runout_count = 5 - len(board_deuces)
        runout_start_index = num_opponents * 2
        board_runout = shuffled_deck[runout_start_index : runout_start_index + board_runout_count]
        final_board = board_deuces + board_runout

        my_rank = evaluator.evaluate(my_hand_deuces, final_board)
        
        all_ranks = [my_rank] + [evaluator.evaluate(opp_hand, final_board) for opp_hand in opponent_hands]
        min_rank = min(all_ranks)
        
        if my_rank == min_rank:
            winners = [rank for rank in all_ranks if rank == min_rank]
            wins += 1 / len(winners)
            
    return (wins / simulations) * 100

# --- API Endpoint with "Airbag" ---
@app.route("/api/evaluate", methods=["POST", "OPTIONS"])
def evaluate():
    try:
        data = request.get_json(force=True)
        my_hand_str = data.get('my_hand', [])
        board_str = data.get('board', [])
        players = data.get('players', 2)
        num_opponents = players - 1

        if len(my_hand_str) != 2:
            raise ValueError("A mão do jogador deve conter exatamente 2 cartas.")

        my_hand_deuces = [to_deuces_card(c) for c in my_hand_str]
        board_deuces = [to_deuces_card(c) for c in board_str]

        # Garantir que não há cartas duplicadas
        all_cards = my_hand_str + board_str
        if len(all_cards) != len(set(all_cards)):
            raise ValueError("Cartas duplicadas detectadas.")

        equity = 0
        suggestion = "Fold"
        hand_strength = ""

        if len(board_str) == 0: # Pre-flop
            score = get_chen_score(my_hand_deuces)
            hand_strength = f"Força Pré-Flop (Chen): {score}"
            if score >= 10: suggestion = "Raise"
            elif score >= 8: suggestion = "Call"
            else: suggestion = "Fold"
            equity = run_monte_carlo(my_hand_deuces, board_deuces, num_opponents, simulations=2000) # Equity pré-flop precisa de mais sims
        
        elif len(board_str) in [3, 4, 5]: # Post-flop
            equity = run_monte_carlo(my_hand_deuces, board_deuces, num_opponents)
            hand_class = evaluator.get_rank_class(evaluator.evaluate(my_hand_deuces, board_deuces))
            hand_strength = evaluator.class_to_string(hand_class)

            fair_share = 100 / players
            if equity > fair_share + 20: suggestion = "Raise High"
            elif equity > fair_share + 10: suggestion = "Raise Low"
            elif equity > fair_share: suggestion = "Call"
            else: suggestion = "Fold"
        
        else:
             raise ValueError("O board deve conter 0, 3, 4 ou 5 cartas.")

        # Construindo a resposta padronizada
        result = {
            "equity": round(equity, 2),
            "suggestion": suggestion,
            "hand_strength": hand_strength
        }
        
        # Mantendo compatibilidade com "result" aninhado
        response_data = {
            "ok": True,
            **result,
            "result": result
        }
        return jsonify(response_data)

    except Exception as e:
        tb = traceback.format_exc()
        app.logger.error(f"Erro em /api/evaluate: {str(e)}\n{tb}")
        return jsonify({"ok": False, "error": str(e), "traceback": tb}), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
