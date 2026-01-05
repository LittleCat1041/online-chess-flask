import chess
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app, cors_allowed_origins="*")

# Game state 
'''Note: Using global variables for a simple Proof of Concept. 
ถ้าอยากเพิ่มห้องเล่นสามารถใช้ Database เพื่อ handle หลายๆห้อง'''
board = chess.Board()
players = {}                
game_started = False
room_id = 'chess_room'
new_game_requests = set()  

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Socket events
@socketio.on('connect')
def handle_connect():
    global game_started

    if len(players) >= 2:
        emit('status', {'message': 'The game is full. You are a spectator.'}, room=request.sid)
        return

    color = 'white' if len(players) == 0 else 'black'
    players[request.sid] = color
    join_room(room_id)

    emit('player_assigned', {'color': color}, room=request.sid)
    emit('status', {'message': f'You are {color.capitalize()}.'}, room=request.sid)

    if len(players) == 2 and not game_started:
        game_started = True
        emit('game_start', {'fen': board.fen(), 'turn': 'w'}, room=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    global game_started
    if request.sid in players:
        leave_room(room_id)
        del players[request.sid]
        game_started = False
        board.reset()
        new_game_requests.clear()
        emit('status', {'message': 'Opponent disconnected. Game reset.'}, room=room_id)
        emit('enable_new_game', room=room_id)


@socketio.on('move')
def handle_move(data):
    global game_started
    if not game_started:
        emit('status', {'message': 'The game has not started yet.'}, room=request.sid)
        return

    move_uci = data['move']
    player_color = players.get(request.sid)

    try:
        move = chess.Move.from_uci(move_uci)
    except ValueError:
        emit('status', {'message': 'Invalid move format.'}, room=request.sid)
        return

    if ((player_color == 'white' and board.turn == chess.WHITE) or
        (player_color == 'black' and board.turn == chess.BLACK)):
        
        # ตรวจสอบอีกครั้งว่าการเดินนี้ถูกกติกาจริงหรือไม่ เพื่อป้องกันการโกงจากฝั่ง Client
        if move in board.legal_moves:
            board.push(move)
            emit('board_update', {'fen': board.fen(),
                                  'turn': 'w' if board.turn == chess.WHITE else 'b'}, room=room_id)

            # Check game over
            if board.is_checkmate():
                emit('game_over', {'result': 'checkmate', 'winner': player_color}, room=room_id)
                board.reset()
                game_started = False
                emit('enable_new_game', room=room_id)
            elif board.is_stalemate():
                emit('game_over', {'result': 'stalemate'}, room=room_id)
                board.reset()
                game_started = False
                emit('enable_new_game', room=room_id)
            elif board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
                emit('game_over', {'result': 'draw'}, room=room_id)
                board.reset()
                game_started = False
                emit('enable_new_game', room=room_id)
        else:
            emit('status', {'message': 'Invalid move.'}, room=request.sid)
    else:
        emit('status', {'message': "It's not your turn."}, room=request.sid)

# New game request (mutual agreement)
@socketio.on('request_new_game')
def handle_new_game_request():
    if request.sid not in players:
        return

    new_game_requests.add(request.sid)
    emit('status', {'message': 'You requested a new game. Waiting for opponent...'}, room=request.sid)
    emit('waiting_for_opponent', room=room_id)

    if len(new_game_requests) == 2:
        board.reset()
        global game_started
        game_started = True
        new_game_requests.clear()
        emit('new_game_ready', {'fen': board.fen(), 'turn': 'w'}, room=room_id)
        emit('status', {'message': 'New game started! White moves first.'}, room=room_id)


# Forfeit handler
@socketio.on('forfeit')
def handle_forfeit():
    global game_started
    if request.sid not in players or not game_started:
        return

    player_color = players[request.sid]
    opponent_sid = next((sid for sid in players if sid != request.sid), None)

    if opponent_sid:
        opponent_color = players[opponent_sid]
        emit('game_over', {'result': 'forfeit', 'winner': opponent_color}, room=room_id)
    else:
        emit('game_over', {'result': 'forfeit', 'winner': player_color}, room=request.sid)

    board.reset()
    game_started = False
    emit('enable_new_game', room=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)
