

class Player:
    def __init__(self, name, position, id):
        #self.G = city_graph
        self.id = id  # this is the session ID for the player
        self.player_index = -1 # todo should probably initialize this on create
        self.mrx = False
        self.detective = True
        self.role = 'Detective'
        self.name = name
        self.color = '#00FF00'  # default color TODO: iterate through a color list as players are added
        self.position = position  # Initial position of the player
        self.tickets = {'taxi': 10, 'bus': 8, 'underground': 4, 'ferry': 0}
        #self.tickets = {'taxi': 25, 'bus': 25, 'underground': 25, 'ferry': 0}
        self.my_turn = False
        self.move_log = []

        print(f'Player {self.name} ({self.player_index=}) created at starting location {self.position}')


    def get_current_state(self):
        state = {'name': self.name,
                 'player_index': self.player_index,
                 'role': self.role,
                 'position': self.position,
                 'tickets': self.tickets
                 }

        return state

    def update_move_log(self, destination, mode):
        print('updating move log: ', destination, mode)
        self.move_log.append({'destination': destination, 'mode': mode})

    def potential_destinations(self, city_graph):
        #pm = city_graph.edges(self.position, data=True)

        destinations_set = set()

        for u, v, data in city_graph.edges(self.position, data=True):
            if u == self.position:
                if self.tickets[data['mode']] > 0:
                    # don't return destinations requiring tickets you don't have
                    destinations_set.add((v, data['mode']))

                else:
                    print(f'{data["mode"]} routes are not available because you have no {data["mode"]} tickets remaining.')

        destinations = [{'destination': dest, 'mode': mode} for dest, mode in destinations_set]

        print(f'Possible destinations/modes: {destinations}')
        return destinations

    def move(self, new_position, transportation_mode, city_graph):
        # Basic move method, can be overridden
        print(f'Attempting to move {self.name} from {self.position} to {new_position} via {transportation_mode}')

        moved = False

        # Check for existence of a path
        if city_graph.has_edge(self.position, new_position):
            pass
        else:
            print(f'Stop {new_position} is unreachable from  {self.position}.')
            return False

        # Check if player even has a ticket for the requested mode
        if self.tickets[transportation_mode] <= 0:
            print(f'{self.name} has no {transportation_mode} tickets remaining.')
            return False

        # one last check to verify that the move & mode are viable
        # could check for sufficient tickets here....
        for u, v, attributes in city_graph.edges([self.position, new_position], data=True):
            if u == self.position and v == new_position and attributes['mode'] == transportation_mode:

                self.position = new_position
                self.tickets[transportation_mode] += -1

                self.update_move_log(new_position, transportation_mode)

                return True

            else:
                pass
                #print('wrong loc or mode, do not care.')

        if not moved:
            print(f"unable to move from {self.position} to {new_position} via {transportation_mode}")
            print(f'{self.name} remains at Stop Number {self.position}')
            return False

    def check_for_available_moves(self, detective_positions, city_graph):
        possible_moves = city_graph.edges(self.position)
        #print(possible_moves)
        return True

    def show_location(self, fig):
        pass


class Detective(Player):
    def check_for_victory(self, mrx_position):
        if self.position == mrx_position:
            print (f"GAME OVER, {self.name} wins!")
            exit(0)

    def check_for_available_moves(self, detective_positions, city_graph):
        possible_destinations = []
        for x in city_graph.edges(self.position):
            possible_destinations.append(x[1])

        #detective_positions.append(self.position)
        #possible_destinations.append(self.position)

        available_moves = list(set(detective_positions)) # - set(possible_destinations))
        print(f'These are your available_moves: {available_moves}')

        if available_moves == []:
            return False
        else:
            return True

class MrX(Player):
    def __init__(self, name, position, id):
        super().__init__(name, position, id)
        #self.G = city_graph
        self.mrx = True
        self.detective = False
        self.visible_location = False
        self.my_turn = True

        self.tickets = {'taxi': 25, 'bus': 25, 'underground': 25, 'ferry': 2, '2xMove': 2}

    def potential_destinations(self, city_graph, detective_locations):
        #pm = city_graph.edges(self.position, data=True)

        destinations_set = set()

        for u, v, data in city_graph.edges(self.position, data=True):
            if u == self.position:
                if self.tickets[data['mode']] > 0:
                    # don't return destinations requiring tickets you don't have
                    destinations_set.add((v, data['mode']))

                else:
                    print(f'{data["mode"]} routes are not available because you have no {data["mode"]} tickets remaining.')

        # ok this doesn't work because it takes mode into account.
        print(f'your possible moves: {destinations_set}....detectives are at {detective_locations}')
        available = destinations_set - set(detective_locations)
        print(f'your available moves are {available}')

        #destinations = [{'destination': dest, 'mode': mode} for dest, mode in destinations_set]
        destinations = [{'destination': dest, 'mode': mode} for dest, mode in available]

        print(f'Possible destinations/modes: {destinations}')
        return destinations


    def update_visibility(self, round):
        print(f'Updating visibility during {round=}')
        if round in [2, 7, 12, 17, 23]:
            print('this is a visible round')
            self.visible_location = True
        else:
            print('this is NOT a visible round')
            self.visible_location = False


    def check_for_win(self, round):
        if round >= 24:
            print('Game over after 24 rounds!')
            return True
        else:
            return False


    def check_for_available_moves(self, detective_positions, city_graph):
        possible_destinations = []
        for x in city_graph.edges(self.position):
            possible_destinations.append(x[1])

        detective_positions.append(self.position)
        possible_destinations.append(self.position)

        available_moves = list(set(detective_positions) - set(possible_destinations))
        print(f'These are your available_moves: {available_moves}')

        if available_moves == []:
            return False
        else:
            return True
