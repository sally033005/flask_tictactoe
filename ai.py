import math, random

def is_winner(board, player):
    win_patterns = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    return any(all(board[i] == player for i in combo) for combo in win_patterns)

def is_draw(board):
    return all(cell != ' ' for cell in board)

def minimax(board, depth, is_maximizing):
    if is_winner(board, 'O'):
        return 1
    elif is_winner(board, 'X'):
        return -1
    elif is_draw(board):
        return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                score = minimax(board, depth + 1, False)
                board[i] = ' '
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                score = minimax(board, depth + 1, True)
                board[i] = ' '
                best_score = min(score, best_score)
        return best_score

def best_move(board, difficulty="hard"):
    """Return the best AI move based on difficulty level."""
    available = [i for i, v in enumerate(board) if v == ' ']

    # --- Easy mode: random move
    if difficulty == "easy":
        return random.choice(available)

    # --- Medium mode: 50% chance random, 50% minimax
    if difficulty == "medium":
        if random.random() < 0.5:
            return random.choice(available)

    # --- Hard mode (default): full minimax
    best_score = -math.inf
    move = None
    for i in available:
        board[i] = 'O'
        score = minimax(board, 0, False)
        board[i] = ' '
        if score > best_score:
            best_score = score
            move = i
    return move
