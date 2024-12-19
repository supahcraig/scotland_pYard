# scotland_pYard
A web-based multi-player implemenation of the classic board game Scotland Yard, using Python, Flask, and SocketIO


## NOTES

Yes, the UI is hideous.   A lot of that is to help visualize the grid within the page.   A lot of it is also that I don't really know css, or UI/UX in general.  The focus was function over form.

## Basic Instructions To Play

### "Install"
clone the repo, install the requirements

### Run the app
`python app.py`

This will create a server on your machine.   Navigate to `localhost:5000/game` to bring up the UI.

You can multiplayer on a single machine, but it will break the spirit of the game.   Other clients can run on other machines, navigate to your server IP instead of localhost.

### Players join the game

Each player will enter their name, pick a color, and hit join game.  The _first_ player to press `Join Game` will play as Mr. X.  All other players will play as a Detective.

### Start the game

The host will have a button labeled `Start Game` which will actually start the game.



## Objective

Detectives attempt to track down Mr. X by moving around the map via various forms of transportation.  The goal is for a detective to land land on the same spot to capture him.  Detectives should play as a team.  

Mr. X is also moving around the map, but he is not visible on the map except during selected turns.  The transportation modes he uses are logged in the move log, so you can start to form educated guesses on his possible locations.


## Game Play

Mr. X always goes first in a round.   He will pick a destination & transport mode and click on the button to make that move.   Detectives will move one by one through the end of the round.  Movement requires a ticket for that transportation mode, so once all your Taxi tickets are used up, you can no longer use taxis to move around.

At various points during the game, Mr. X will reveal his location on the map, which will allow you to zero in on his location.


### End Game
If a detective moves to the same spot as Mr. X, the detectives win and the game is over.

If Mr. X gets through 24 rounds without being caught, Mr. X wins and the game is over.


## TODO log

* incognito move option
* Mr. X's double move is not implemented
* inconsistent way of identifying who is mr.x & who's turn it is (player index, etc)
* map can't be displayed on my laptop screen

### Bigger changes
* The game join/start is clunky, would like to make it a Host/Lobby/Join sort of thing
* if you refresh your browser or navigate away accidentally, you lose the game state
* the turn logic is accidentally recursive, but could probably be done in a for loop
* socket events are sometimes nested, need to unravel that
* responsive design for the UI?
* Allow players to select who is Mr. X
  * IDEA:  have all the players join into a "staging" array, then once mr. x joins actually create the player objects in the correct order (Mr. X being player[0])