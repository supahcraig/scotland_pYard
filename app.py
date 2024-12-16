from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from game import Game
import draw_map

app = Flask(__name__)
socketio = SocketIO(app)

game = Game()


@app.route('/game')
def socket():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    # sends the session ID back to the client
    session_id = request.sid
    print(f'client connected with session id {session_id}')

    emit('session_id', {'session_id': session_id}, broadcast=True)


@socketio.on('join_room')
def handle_join_room(data):
    # all the detectives will join a single room
    room = data['room']
    join_room(room)
    emit('response', {'message': f'You have joined room {room}'}, room=room)


@socketio.on('new_player')
def handle_new_player(data):
    player_sid = request.sid # todo rename this attribute as session_id
    #player_id = data['playerId']
    #player_name = data['playerName']
    #players[player_id] = player_name

    # grab the specific player we just created
    # function returns the number of players currently in the game, so the index is 1 less than that
    i = game.create_player(data['playerName'], player_sid) - 1

    print(f'joined as player # {i}')

    p = game.players[i]
    p.player_index = i
    print(f'{p.name} has session id={p.id}')

    if p.mrx:
        role = 'Mr. X'
        p.my_turn = True

    elif p.detective:
        role = 'Detective'
        p.my_turn = False
    else:
        role = 'UNKNOWN'

    emit('initial_player_state', {'location': p.position,
                                  'role': role,
                                  'player_index': p.player_index
    }, room=p.id)


def initialize_board():
    print(f'Initializing board...')

    for p in game.players:
        print(f'initializing for {p.name}')
        emit('initialize', {'player': p.get_current_state()}
            , room=p.id
        )



@socketio.on('start_game')
def start_game(_):
    print('starting game...')

    # starting game is really making a few things visible, and then just initiating a round
    # generate a new map with the initial positions

    # this will generate new maps, and then the page will refresh it
    draw_map.generate_new_map(game.players, game.G)

    initialize_board()

    #emit('initial_map', { }, broadcast=True)  # moved this to the initialize function on the page

    initiate_turn()


#@socketio.on('initiate_turn')
def initiate_turn():
    print('initiating turn...')
    # send waiting message & potential moves to other players
    # send possible moves to current player & render on screen

    # new map needs to be generated at the top of each round, in case Mr X is visible during that round
    # could probably do this selectively based on the round, but it's lightweight.
    draw_map.generate_new_map(game.players, game.G)

    emit('update_map', {'mrx_move_log': game.players[0].move_log }, broadcast=True)

    for p in game.players:
        if not p.my_turn:
            emit('waiting', {'waiting_on': game.players[game.current_turn_index].name,
                             'potentialMovesList': p.potential_destinations(game.G),
                             },
                 room=p.id)

        else:
            available_moves = p.potential_destinations(game.G)
            if available_moves != []:
                emit('your_turn', {'potentialMovesList': p.potential_destinations(game.G),
                                   },
                     room=p.id)
            else:
                print(f'No moves available for {p.name}')

                # watch out, this is gonna get recursive too
                game.increment_turn()
                initiate_turn()


@socketio.on('player_move')
def handle_move(move):
    print('player move requested:', move['destination'], move['mode'])

    game.players[game.current_turn_index].move(move['destination'], move['mode'], game.G)

    # send the updated ticket inventory to the page
    update_tickets()

    # generate a new map with updated locations after the move completes
    draw_map.generate_new_map(game.players, game.G)

    # fire the event to tell the page to reload the new image
    emit('update_map', {'mrx_move_log': game.players[0].move_log }, broadcast=True)

    # check for win
    if game.round_number >= 24:
        emit('game_over', {'win_message': 'Mr. X has eluded the authorities!'}, broadcast=True)

        # todo have the app fire the end_game event
        exit(99)

    elif game.check_for_win():
        emit('game_over', {'win_message': 'Mr. X has been apprehended!'}, broadcast=True)

        # todo have the app fire the end_game event
        exit(99)

    else:
        pass

    game.increment_turn()

    # this will end up being massively recursive, which isn't what we want
    initiate_turn()


def update_tickets():
    ticket_inventory = [t.tickets for t in game.players if not t.mrx]
    ticket_inventory = [{'name': t.name, 'tickets': t.tickets} for t in game.players if not t.mrx ]
    print(ticket_inventory)

    emit('update_tickets', {'ticket_inventory': ticket_inventory})


@socketio.on('end_game')
def handle_end_game(_):
    print('ending game')
    exit(99)


@socketio.on('message')
def handle_message(data):
    # Broadcast message to all players
    emit('message', data, broadcast=True)



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
