from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import string

app = Flask(__name__)
app.secret_key = "tictactoe_secret_key"

# Store multiple active games
games = {}

# --- Helper functions ---
def new_board():
    return [' '] * 9

def check_winner(board):
    wins = [
        (0,1,2), (3,4,5), (6,7,8),
        (0,3,6), (1,4,7), (2,5,8),
        (0,4,8), (2,4,6)
    ]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] and board[a] != ' ':
            return board[a]
    return None

def check_draw(board):
    return ' ' not in board and not check_winner(board)

def random_ai_move(board):
    available = [i for i, v in enumerate(board) if v == ' ']
    return random.choice(available)

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup():
    mode = request.form.get('mode')
    session['mode'] = mode
    session['wins'] = {'X': 0, 'O': 0}
    if mode == '1':
        return render_template('setup.html', mode='1')
    else:
        return render_template('setup.html', mode='2')

@app.route('/start', methods=['POST'])
def start():
    mode = session.get('mode')
    if mode == '1':
        player_name = request.form.get('player_name')
        session['player_name'] = player_name
        session['ai_name'] = 'Computer'
        session['board'] = new_board()
        session['current'] = 'X'
        session['wins'] = {'X': 0, 'O': 0}
        return redirect(url_for('game'))
    else:
        player_name = request.form.get('player_name')
        code = generate_code()
        games[code] = {
            'players': {'X': player_name, 'O': None},
            'board': new_board(),
            'current': 'X',
            'wins': {'X': 0, 'O': 0}
        }
        session['code'] = code
        session['player_symbol'] = 'X'
        return redirect(url_for('game_room', code=code))

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')
    else:
        code = request.form.get('code').strip().upper()
        player_name = request.form.get('player_name')
        if code not in games:
            return render_template('join.html', error="Invalid code.")
        if games[code]['players']['O'] is not None:
            return render_template('join.html', error="Game is full.")
        games[code]['players']['O'] = player_name
        session['code'] = code
        session['player_symbol'] = 'O'
        return redirect(url_for('game_room', code=code))

@app.route('/game')
def game():
    mode = session.get('mode')
    board = session.get('board', new_board())
    current = session.get('current', 'X')
    winner = check_winner(board)
    draw = check_draw(board)
    player_name = session.get('player_name')
    ai_name = session.get('ai_name')
    wins = session.get('wins', {'X':0, 'O':0})
    return render_template('game.html', 
                           mode=mode, 
                           board=board, 
                           current=current,
                           winner=winner, 
                           draw=draw,
                           player_name=player_name,
                           ai_name=ai_name,
                           wins=wins)

@app.route('/move/<int:cell>')
def move(cell):
    mode = session.get('mode')

    # --- 1 Player Mode ---
    if mode == '1':
        board = session['board']
        wins = session['wins']
        current = session['current']

        # Player move
        if board[cell] == ' ' and not check_winner(board) and not check_draw(board):
            board[cell] = 'X'
            winner = check_winner(board)
            if winner:
                wins[winner] += 1
                session['wins'] = wins
                session['board'] = board
                return redirect(url_for('game'))

            if not check_draw(board):
                # AI move
                ai_move = random_ai_move(board)
                board[ai_move] = 'O'
                winner = check_winner(board)
                if winner:
                    wins[winner] += 1

        session['wins'] = wins
        session['board'] = board
        return redirect(url_for('game'))

    # --- 2 Player Mode ---
    else:
        code = session.get('code')
        player_symbol = session.get('player_symbol')
        if not code or code not in games:
            return "Invalid game code."
        game = games[code]
        board = game['board']

        if game['current'] == player_symbol and board[cell] == ' ':
            board[cell] = player_symbol
            winner = check_winner(board)
            if winner:
                game['wins'][winner] += 1
            elif not check_draw(board):
                game['current'] = 'O' if player_symbol == 'X' else 'X'

        return redirect(url_for('game_room', code=code))

@app.route('/room/<code>')
def game_room(code):
    if code not in games:
        return "Invalid room code."

    game = games[code]

    # If Player 2 hasn't joined, show waiting page
    if game['players']['O'] is None:
        return render_template('waiting.html', code=code)

    # Both players are present, show the game board
    return render_template('game.html',
                           mode='2',
                           board=game['board'],
                           current=game['current'],
                           winner=check_winner(game['board']),
                           draw=check_draw(game['board']),
                           player_name=game['players']['X'],
                           ai_name=game['players']['O'],
                           wins=game['wins'],
                           code=code)

@app.route('/reset')
def reset():
    mode = session.get('mode')
    if mode == '1':
        session['board'] = new_board()
        session['current'] = 'X'
    else:
        code = session.get('code')
        if code in games:
            games[code]['board'] = new_board()
            games[code]['current'] = 'X'
    return redirect(url_for('game' if mode == '1' else 'game_room', code=session.get('code')))

@app.route('/game_state/', defaults={'code': None})
@app.route('/game_state/<code>')
def game_state(code):
    mode = session.get('mode')

    if mode == '1':
        board = session.get('board', new_board())
        current = session.get('current', 'X')
        winner = check_winner(board)
        draw = check_draw(board)
        wins = session.get('wins', {'X': 0, 'O': 0})
        return jsonify({
            'board': board,
            'current': current,
            'winner': winner,
            'draw': draw,
            'wins': wins,
            'player_name': session.get('player_name'),
            'ai_name': session.get('ai_name')
        })
    else:
        if not code or code not in games:
            return jsonify({'error': 'Invalid game code'}), 404
        game = games[code]
        return jsonify({
            'board': game['board'],
            'current': game['current'],
            'winner': check_winner(game['board']),
            'draw': check_draw(game['board']),
            'wins': game['wins'],
            'players': game['players']
        })

if __name__ == '__main__':
    app.run(debug=True)