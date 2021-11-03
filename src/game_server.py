import time
from board import Board
import threading
import socket
from client_protocol import Protocol_client
from ai import AI
from enums import Squares as sq
from enums import Directions as dir
from consts import *

strDir = { '0' : dir.RIGHT, '1' : dir.UP, '2' : dir.LEFT, '3' : dir.DOWN }
dirStr = { dir.RIGHT : '0', dir.UP : '1', dir.LEFT : '2', dir.DOWN : '3' }

strPlayer = { '1' : sq.P1, '2' : sq.P2 }
playerStr = { sq.P1 : '1', sq.P2 : '2' }

class Game:
    def __init__( self, n_players, n_ais ):
        self.board = Board( N )
        self.running = True

        self.lock = threading.Lock()

        self.ready = False
        self.n_connections = 0
        self.connections = []
        self.AIs = []

        self.n_players = n_players
        self.n_ais = n_ais
        self.last_msg = { sq.P1 : '1110', sq.P2 : '2120' }

        self.server = socket.socket()
        HOST = socket.gethostbyname( socket.gethostname() )
        PORT = 5050
        self.server.bind( (HOST, PORT) )

    def assign_players( self ):
        if( self.ready ): return 0

        print("[PLAYERS CONNECTED] assigning players to its avatars")
        for player_number in range( self.n_players ):
            assign_msg = str(player_number + 1) + "***"
            self.connections[ player_number ].send( assign_msg.encode('utf-8') )

        for player_number in range( self.n_players, self.n_players + self.n_ais ):
            assign_msg = str(player_number + 1) + "***"
            self.AIs[ player_number - self.n_players ].assign_player( assign_msg )

        self.ready = True

    def store_dir( self, msg ):
        who_moved = strPlayer[ msg[2] ]
        self.last_msg[ who_moved ] = msg

    def handle_player( self, conn, addr ):
        print("[NEW CONNECTION]" + str(addr[0]) + ":" + str(addr[1]) + " connected")

        while( self.n_connections < self.n_players + self.n_ais ):
            pass

        self.lock.acquire()
        self.assign_players()
        self.lock.release()

        remainder_msg = ""
        while( True ):
            print("[LISTENING] waiting on user moves...")
            bytes_received = len( remainder_msg )
            client_msg = remainder_msg
            remainder_msg = ""

            while( bytes_received < PROTOCOL_SIZE ):
                tmp_msg, player_addr = conn.recvfrom( PROTOCOL_SIZE )
                tmp_msg = tmp_msg.decode('utf-8')
                bytes_received += len(tmp_msg)
                client_msg += tmp_msg

            if( len(client_msg) > PROTOCOL_SIZE ):
                remainder_msg = client_msg[PROTOCOL_SIZE:]
                client_msg = client_msg[:PROTOCOL_SIZE]

            if( client_msg == "****" ): break
            print(client_msg)
            self.lock.acquire()

            self.store_dir( client_msg )

            self.lock.release()

            if( not self.running ): break

        return 0

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
        game_status = self.board.move( player=who_moved, nxt_direction=dir_idx )
        if( game_status == 1 ):
            end_game = False

        self.running = not end_game
        return ( destination, int( dirStr[ dir_idx ] ), who_moved, end_game )

    def simulate( self ):
        for ai_player in self.AIs:
            ai_move = ai_player.start()
            self.store_dir( ai_move )

        for player in playerStr.keys():
            if( not self.running ): return 0

            destination, dir_idx, player, end_game = self.process_input( self.last_msg[ player ] )
            server_msg = self.build_message( destination, dir_idx, player, end_game )

            for player_number in range( 0, len(self.connections) ):
                player_move = str( player_number + 1 ) + server_msg
                self.send_move( self.connections[ player_number ], player_move )

            for player_number in range( self.n_players, self.n_players + self.n_ais ):
                player_move = str( player_number + 1 ) + server_msg
                self.AIs[ player_number - self.n_players ].process_input( player_move )

    def run( self ):
        print("[WAITING] Waiting for connections...")
        self.server.listen()
        thread_list = []
        while( len(self.connections) < self.n_players ):
            conn, addr = self.server.accept()
            thread = threading.Thread( target=self.handle_player, args=( conn, addr ) )
            thread_list.append( thread )
            self.n_connections += 1
            thread.name = "player" + str(self.n_connections)
            self.connections.append(conn)
            thread.start()

        while( len(self.AIs) < self.n_ais ):
            self.lock.acquire()
            self.AIs.append( AI() )
            self.n_connections += 1
            self.lock.release()


        while( not self.ready ):
            pass

        time_frame = 0.0
        t1 = time.time()
        while( self.running ):
            time_frame = time.time() - t1

            if( time_frame >= TIME_STEP ):
                self.lock.acquire()
                self.simulate()
                self.lock.release()

                t1 = time.time()

        for t in thread_list:
            t.join()
        print("[GAME OVER] Turning off server...")
