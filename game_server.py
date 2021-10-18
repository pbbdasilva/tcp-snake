from board import Board
import threading
import socket
from client_protocol import Protocol_client
from enums import Squares as sq
from enums import Directions as dir

N = 20
strDir = { '0' : dir.RIGHT, '1' : dir.UP, '2' : dir.LEFT, '3' : dir.DOWN }
dirStr = { dir.RIGHT : '0', dir.UP : '1', dir.LEFT : '2', dir.DOWN : '3' }

strPlayer = {'1' : sq.P1, '2' : sq.P2 }
playerStr = { sq.P1 : '1', sq.P2 : '2' }

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
            bytes_received = 0
            client_msg = ""

            while(bytes_received < 4):
                tmp_msg, player_addr = conn.recvfrom( 4 )
                tmp_msg = tmp_msg.decode('utf-8')
                bytes_received += len(tmp_msg)
                client_msg += tmp_msg

            print(client_msg)
            self.lock.acquire()

            destination, dir_idx, player, end_game = self.process_input( client_msg )
            server_msg = self.build_message( destination, dir_idx, player, end_game )

            for player_number in range(0, len(self.connections)):
                player_move = str(player_number + 1) + server_msg
                self.send_move( self.connections[ player_number ], player_move )

            self.lock.release()

            if(end_game): return 0

    def build_message( self, destination, dir_idx, player, end_game ):
        protocol = Protocol_client( destination=destination, direction=dir_idx, end_game=end_game, who=player )
        return str( protocol )

    def send_move( self, conn, server_msg ):
        conn.send( server_msg.encode('utf-8') )

    def process_input( self, msg ):
        destination = strPlayer[ msg[0] ]
        dir_idx = strDir[ msg[1] ]
        who_moved = strPlayer[ msg[2] ]

        end_game = True
        game_status = self.board.move( who_moved, dir_idx )
        if( game_status == 1 ):
            end_game = False

        return ( destination, dir_idx, who_moved, end_game )

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
