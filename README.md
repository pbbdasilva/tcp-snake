# tcp-snake

Multiplayer game using tcp networking protocol inspired by the TRON game. The goal is to make your opponent hit your trail.

## Install

Run ```setup.sh``` with sudo privileges.

## Play
The game has 2 modes, PvP or PvsAI.
- PvP requires 2 players(clients) and a server. Hence, you should execute the game as a client 2 times using ```python3 src/client.py``` and once using ```python3 src/server.py```.
- PvsAI you only need 1 client. You will need to execute ```python3 src/server.py``` once again but keep in mind to choose how many AIs you want at your game and how many real players. You may change it at the init parameters of the server.Game class. (1,1) for PvsAI and (2,0) for PvP.

## How it works

Both server and client use a multi-threaded environment due to blocking IO. So, to avoid race conditions, we used a mutex lock to updated variables that were shared by the threads.

### Server

The main thread listen for new connections until it reaches the desired number of players. The IO from players is handled separated at each thread. Whilst, the game simulation runs at the main thread and updates the board after each TIME_STEP. The server has authority towards moves, hence, each move from a player is only updated after the server process the move.

### Client

The main thread awaits for player inputs and render the game board at constant FPS (possible due to lightweight interface). At the same time, there is a second thread listening to IO from server to update the board.

### AI

The AI heuristic is to always make moves that let it have "more free space". Free space is defined as squares that the AI is able to reach before the other player, this is calculated using **multisource BFS**. After this, we use **Flood Fill** to count the area of [Voronoi Partitions](https://en.wikipedia.org/wiki/Voronoi_diagram) of our current board.
