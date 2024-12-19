from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from game import Game
import draw_map

app = Flask(__name__)
socketio = SocketIO(app)

game = Game()


@app.route('/')
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
    player_sid = request.sid # todo rename this attribute as session_id // huh?  looks like it's already clearly named


    # grab the specific player we just created
    # function returns the number of players currently in the game, so the index is 1 less than that
    i = game.create_player(data['playerName'], player_sid) - 1

    print(f'joined as player # {i}')

    p = game.players[i]
    p.player_index = i
    p.color = data['playerColor']
    print(f'{p.name} has session id={p.id}')  # todo: the above comment is referring to the player attribute "id"

    if p.mrx:
        p.role = 'Mr. X'
        p.my_turn = True

    elif p.detective:
        p.role = 'Detective'
        p.my_turn = False
    else:
        role = 'UNKNOWN'

    emit('initial_player_state', {'location': p.position,
                                  'role': p.role,
                                  'player_index': p.player_index,
    }, room=p.id)

    emit('player_added', {'name': p.name,
                          'color': p.color,
                          'role': p.role,
    },   broadcast=True)


@socketio.on('color_change')
def handle_color_change(data):
    print('Somebody changed their color...')
    print(data)

    game.players[data['player_index']].color = data['new_color']

    # send the new color to all the other players
    emit('update_color', {'name': game.players[data['player_index']].name,
                          'new_color': data['new_color']
    }, broadcast=True)


def initialize_board():
    print(f'Initializing board...')

    for p in game.players:
        print(f'initializing for {p.name}')
        emit('initialize', {'player': p.get_current_state()}
            , room=p.id
        )


def initialize_ticket_grid():
    print(f'Initializing the ticket grid for all players....')

    players = [{'name': p.name, 'index': p.player_index, 'color': p.color} for p in game.players if not p.mrx]

    emit('initialize_ticket_grid', {'players': players}, broadcast=True)


@socketio.on('start_game')
def start_game(_):
    print('starting game...')

    # starting game is really making a few things visible, and then just initiating a round
    # generate a new map with the initial positions

    # this will generate new maps, and then the page will refresh it
    draw_map.generate_new_map(game.players, game.G)

    # this initializes the board for each player
    initialize_board()

    # this doesn't update the tickets, just the player grid itself
    initialize_ticket_grid()

    # this updates the grid with the current ticket counts
    update_tickets()

    #emit('initial_map', { }, broadcast=True)  # moved this to the initialize function on the page

    initiate_turn()


#@socketio.on('initiate_turn')
def initiate_turn():
    print('initiating turn...')
    # send waiting message & potential moves to other players
    # send possible moves to current player & render on screen

    # new map needs to be generated at the top of each round, in case Mr X is visible during that round
    # PROBLEM: need to have mrx location only be visible during their turn (probably need to show the stop # in the log)
    draw_map.generate_new_map(game.players, game.G)

    emit('update_map', {'mrx_move_log': game.players[0].move_log }, broadcast=True)

    for p in game.players:
        if p.mrx:
            detective_locations = [x.position for x in game.players if not x.mrx]
            available_moves = p.potential_destinations(game.G, detective_locations)
        else:
            available_moves = p.potential_destinations(game.G)
        if not p.my_turn:
            emit('waiting', {'waiting_on': game.players[game.current_turn_index].name,
                             'potentialMovesList': available_moves,
                             },
                 room=p.id)

        else:
            if available_moves != []:
                emit('your_turn', {'potentialMovesList': available_moves,
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
    # if we also update the map at the top of the initiate_turn call, why is it also needed here?  IT ISN'T
    #draw_map.generate_new_map(game.players, game.G)

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
    ticket_inventory = [{'name': t.name, 'tickets': t.tickets} for t in game.players if not t.mrx ]
    print(ticket_inventory)

    emit('update_tickets', {'ticket_inventory': ticket_inventory}, broadcast=True)


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
