import csv
import networkx as nx
import random
from Player import Detective, MrX
import draw_map


class Game:
    def __init__(self):
        self.players = []

        # initial conditions
        self.starting_locations = [13, 26, 29, 34, 50, 53, 91, 94, 103, 112, 117, 132, 138, 141, 155, 174, 197, 198]
        random.shuffle(self.starting_locations)

        # move number when Mr X must reveal his location
        location_reveals = [3, 8, 13, 18, 24]

        self.G = self.create_city_graph('stop_defs.csv')

        draw_map.generate_new_map(self.players, self.G)

        self.current_turn_index = 0
        self.round_number = 1
        self.turn_number = 0

    def get_game_state(self):
        pass

    def create_city_graph(self, stop_defs_file):
        # Create the graph (a simple example of London locations)
        G = nx.MultiGraph()

        # Create a node per entry in the grid locations file
        # append the coordinates to each node
        with open('grid_locations.txt') as f:
            reader = csv.reader(f)
            next(reader)

            for row in reader:
                stop_number = int(row[0])
                x = float(row[1])
                y = float(row[2])

                G.add_node(stop_number, coords=(x, y))

        # Create edges between each stop, for each valid mode between those stops
        with open(stop_defs_file) as f:
            reader = csv.reader(f)
            next(reader)  # skip header row

            for stop in reader:
                node1, node2, mode = int(stop[0]), int(stop[1]), stop[2].strip()
                G.add_edge(node1, node2, mode=mode)

        return G

    def create_player(self, name, id):
        # general idea here is that we previously randomized the starting locations
        # then each player's starting location will be the next element in that list,
        # and we'll use the current numbers of players as the location index
        # rather than selecting one at random and checking to see if it was already selected

        # The first person to join will be Mr X, so player[0] will always be Mr. X
        # todo would be nice to not require Mr. X to be the first one to join the game
        if len(self.players) == 0:
            #self.players.append(MrX(name=name, position=118, id=id))
            self.players.append(MrX(name=name, position=self.starting_locations[len(self.players)], id=id))
            print(f'{name} has joined the game as Mr X.')

        else:
            #self.players.append(Detective(name=name, position=91, id=id))
            self.players.append(Detective(name=name, position=self.starting_locations[len(self.players)], id=id))
            print(f'{name} has joined the game as a detective.')

        return len(self.players) # as a proxy for player ID


    def move_player(self, player_id, new_position, mode):
        p = self.players[player_id]
        return p.move(new_position=new_position, transportation_mode=mode, city_graph=self.G)

    def check_for_win(self):
        print(f'checking for win on {self.round_number=}')

        # check if Mr X is in the same location as the current player
        detective_positions = [x.position for x in self.players if not x.mrx]

        if self.players[0].position in detective_positions:
            print("Mr X has been apprehended.  GAME OVER!!!!!")
            return True
        else:
            return False

    def check_for_cornered(self):
        # check to see if Mr. X as any available moves
        # todo implemaent the cornered function, probably better as a mr. x method
        pass


    def increment_turn(self):
        # this is just the raw turn number across all rounds
        self.turn_number += 1

        # this will roll the turn index over whenever the last player goes
        # Sets the "old" current player to NOT MY TURN
        # Then increments the turn index
        # And sets the "new" current player to MY TURN
        self.players[self.current_turn_index].my_turn = False
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
        self.players[self.current_turn_index].my_turn = True


        # Round is incremented once all the players have gone, thanks to the magic of integer division
        self.round_number = self.turn_number // len(self.players)

        print(f'{self.turn_number=}')
        print(f'========================={self.round_number=}')
        print(f'{self.current_turn_index=}')

        self.players[0].update_visibility(self.round_number)


if __name__ == '__main__':
    game = Game()


