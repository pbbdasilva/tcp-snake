import socket
import threading
import time
import sys
from queue import Queue
from board import Board
from copy import deepcopy
from client_protocol import Protocol_client
from enums import Squares as sq
from enums import Directions as dir
from enums import ChangeVolume as vol
from enums import PlayerCaracters as pchar
from consts import *

strDir = { '0' : dir.RIGHT, '1' : dir.UP, '2' : dir.LEFT, '3' : dir.DOWN }
dirStr = { dir.RIGHT : '0', dir.UP : '1', dir.LEFT : '2', dir.DOWN : '3' }

strPlayer = { '1' : sq.P1, '2' : sq.P2 }
playerStr = { sq.P1 : '1', sq.P2 : '2' }

intPchar = { 0 : pchar.OP1, 1 : pchar.OP2, 2 : pchar.OP3, 3 : pchar.OP4 }
pcharInt = { pchar.OP1 : 0, pchar.OP2 : 1, pchar.OP3 : 2, pchar.OP4 : 3 }

dy = [ +1, 0, -1,  0 ]
dx = [ 0, -1,  0, +1 ]
direction_list = [ dir.RIGHT, dir.UP, dir.LEFT, dir.DOWN ]

playerTmp = {sq.P1 : sq.TMP_P1, sq.P2 : sq.TMP_P2 }
adversary = {sq.P1 : sq.P2, sq.P2 : sq.P1 }

class AI:
    def __init__( self , verbose_mode = False ):
        self.running = True
        self.loser = sq.EMPTY
        self.verbose = verbose_mode

        self.player = sq.EMPTY
        self.b = Board( N )

    def update_direction( self, new_direction ):
        self.b.set_direction( new_direction, who=self.player )

    def send_move( self ):
        protocol = Protocol_client( destination=self.player, direction=int( dirStr[ self.b.get_direction( who=self.player ) ] ), who=self.player )
        protocol_msg = playerStr[ self.player ] + str( protocol )

        return protocol_msg

    def process_input( self, msg ):
        dir_idx = strDir[ msg[1] ]
        who_moved = strPlayer[ msg[2] ]

        end_game = True
        game_status = self.b.move( who_moved, dir_idx )
        if( game_status == 1 ):
            end_game = False

        self.running = not end_game
        if( end_game ): self.loser = who_moved

    def assign_player( self, msg ):
        self.player = strPlayer[ msg[0] ]

    def get_moves( self, curr_x, curr_y ):
        candidates = []

        for i in range(4):
            nxt_x = curr_x + dx[i]
            nxt_y = curr_y + dy[i]

            if(nxt_x < 0 or nxt_x >= N): continue
            if(nxt_y < 0 or nxt_y >= N): continue

            candidates.append( ( nxt_x, nxt_y, direction_list[i] ) )

        return candidates

    def dfs( self, color, curr_x, curr_y, board ):
        ans = 1
        self.vis[ curr_x ][ curr_y ] = True
        for nxt_x, nxt_y, nxt_dir in self.get_moves( curr_x, curr_y ):
            if( board[ nxt_x ][ nxt_y ] != color ): continue
            if( self.vis[ nxt_x ][ nxt_y ] ): continue

            ans += self.dfs( color, nxt_x, nxt_y, board )

        return ans

    def get_eval( self, curr_x, curr_y, board ):
        tmp_color = playerTmp[ self.player ]
        adv_color = playerTmp[ adversary[ self.player ] ]
        adv_x, adv_y = self.b.players[ adversary[ self.player ] ].get_coord()

        board[ curr_x ][ curr_y ] = tmp_color
        q = Queue()
        q.put( ( curr_x, curr_y, tmp_color ) )
        q.put( ( adv_x, adv_y, adv_color ) )

        while( not q.empty() ):
            x, y, color = q.get()

            for nxt_x, nxt_y, nxt_dir in self.get_moves( x, y ):
                if( board[ nxt_x ][ nxt_y ] != sq.EMPTY ): continue

                board[ nxt_x ][ nxt_y ] = color
                q.put( ( nxt_x, nxt_y, color ) )

        ans = self.dfs( tmp_color, curr_x, curr_y, board )
        ans -= self.dfs( adv_color, adv_x, adv_y, board )

        return ans

    def start( self ):
        t1 = time.time()

        curr_x, curr_y = self.b.players[ self.player ].get_coord()
        possible_moves = self.get_moves( curr_x, curr_y )

        curr_eval = -10000
        curr_dir = dir.UP
        if( self.verbose ): self.b.show()
        for nxt_x, nxt_y, nxt_dir in possible_moves:
            if( self.b.board[ nxt_x ][ nxt_y ] != sq.EMPTY ): continue

            if( self.verbose ): print(nxt_dir)
            self.vis = [ [ False for _ in range(N) ] for _ in range(N) ]
            tmp_board = deepcopy(self.b.board)
            pos_eval = self.get_eval( nxt_x, nxt_y, tmp_board )
            if( self.verbose ): print("eval was: " + str(pos_eval))
            if( pos_eval > curr_eval ):
                curr_eval = pos_eval
                curr_dir = nxt_dir

        self.update_direction( curr_dir )
        if( self.verbose ): print("sending move..." + str(curr_dir))
        dt = time.time() - t1
        if( self.verbose ): print("time spent: " + str(dt))
        return self.send_move()

def main():
    ai = AI(sq.P2)
    ai.start()

if __name__ == '__main__':
    main()
