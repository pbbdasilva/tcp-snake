from board import Board
import threading
import socket
from client_protocol import Protocol_client

N = 20

class Game:
    def __init__( self, n_players ):
        self.board = Board( N )

        self.lock = threading.Lock()

        self.n_connections = 0
        self.n_players = n_players

        self.server = socket.socket()
        HOST = socket.gethostbyname( socket.gethostname() )
        PORT = 5050
        socket.bind( (HOST, PORT) )

    def handle_player( self, conn, addr ):
        print("[NEW CONNECTION]" + addr[0] + ":" + addr[1] + " connected")

        while( self.n_connections < self.n_players ):
            pass

        while( True ):
            msg, player_addr = conn.recvfrom( 5 ).decode( 'utf-8' )
            if(len(msg) != 0):
                dir_idx, player, end_game = self.process_input( msg, player_addr )

                self.lock.acquire()
                self.update_board()
                self.lock.release()

    def process_input(self, msg, player_addr):
        dir_idx = int( msg[0] )
        player = msg[1]
        end_game = True

        game_status = self.board.move( player, dir_idx )
        if( game_status == 0 ):
            end_game = False

        return ( dir_idx, player, end_game )

    def start( self ):
        print("[WAITING] Waiting for connections...")
        self.server.listen()

        while( True ):
            conn, addr = self.server.accept()
            thread = threading.Thread( target=self.handle_player, args=( conn, addr ) )
            self.n_connections += 1
            thread.name = "player" + str(self.n_connections)
            thread.start()