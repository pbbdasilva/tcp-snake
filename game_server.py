from board import Board
import threading
import socket
from client_protocol import Protocol_client
from enums import Squares as sq
from enums import Directions as dir

N = 20

class Game:
    def __init__( self, n_players ):
        self.board = Board( N )

        self.lock = threading.Lock()

        self.n_connections = 0
        self.connections = []
        self.n_players = n_players

        self.server = socket.socket()
        HOST = socket.gethostbyname( socket.gethostname() )
        PORT = 5050
        self.server.bind( (HOST, PORT) )

    def handle_player( self, conn, addr ):
        print("[NEW CONNECTION]" + str(addr[0]) + ":" + str(addr[1]) + " connected")

        while( self.n_connections < self.n_players ):
            pass

        while( True ):
            client_msg, player_addr = conn.recvfrom( 5 )
            client_msg = client_msg.decode('utf-8')
            if( len(client_msg) != 0 ):
                print(client_msg)
                self.lock.acquire()

                dir_idx, player, end_game = self.process_input( client_msg, player_addr )
                server_msg = self.build_message( dir_idx, player, end_game )
                for client_conn in self.connections:
                    self.send_move( client_conn, server_msg )

                self.lock.release()

                if(end_game): return 0

    def build_message( self, dir_idx, player, end_game ):
        protocol = Protocol_client( dir_idx, end_game, player )
        return str( protocol )

    def send_move( self, conn, server_msg ):
        conn.send( server_msg.encode('utf-8') )

    def process_input( self, msg, player_addr ):
        dir_idx = -1

        if(msg[0] == '0'): dir_idx = dir.RIGHT
        elif(msg[0] == '1'): dir_idx = dir.UP
        elif(msg[0] == '2'): dir_idx = dir.DOWN
        elif(msg[0] == '3'): dir_idx = dir.LEFT
        else: raise ValueError("direction was not one of the default values")

        if(msg[1] == '1'): player = sq.P1
        else: player = sq.P2

        end_game = True

        game_status = self.board.move( player, dir_idx )
        if( game_status == 0 ):
            end_game = False

        return ( dir_idx, player, end_game )

    def run( self ):
        print("[WAITING] Waiting for connections...")
        self.server.listen()

        while( True ):
            conn, addr = self.server.accept()
            thread = threading.Thread( target=self.handle_player, args=( conn, addr ) )
            self.n_connections += 1
            self.connections.append(conn)
            thread.name = "player" + str(self.n_connections)
            thread.start()
