from enums import Squares as sq
from enums import Directions as dir
from player import Player
import math

class Board:
    def __init__( self, size ):
        self.players = { sq.P1 : Player(sq.P1, math.floor(size/2), math.floor(size/4)),
                         sq.P2 : Player(sq.P2, math.floor(size/2), math.floor(3*size/4)) }

        self.size = size
        self.board = self.init_board()

        self.directions = { dir.RIGHT : 0, dir.UP : 1, dir.LEFT : 2, dir.DOWN : 3 }
        self.dx = [ 1, 0, -1,  0 ]
        self.dy = [ 0, 1,  0, -1 ]

    def init_board( self ):
        board = [ [ sq.EMPTY for i in range( self.size ) ] for j in range( self.size ) ]
        board[ math.floor( self.size/2 ) ][ math.floor( self.size/4 ) ] = sq.P1
        board[ math.floor( self.size/2 ) ][ math.floor( 3*self.size/4 ) ] = sq.P2

        return board

    def move( self, player, nxt_direction ):
        curr_x = self.players[ player ].x
        curr_y = self.players[ player ].y

        next_x = curr_x + self.dx[ self.directions[ nxt_direction ] ]
        next_y = curr_y + self.dy[ self.directions[ nxt_direction ] ]

        next_x = max(next_x, 0)
        next_x = min(next_x, self.size - 1)

        next_y = max(next_y, 0)
        next_y = min(next_y, self.size - 1)

        if ( self.board[ next_x ][ next_y ] != sq.EMPTY ):
            return 0

        self.board[ next_x ][ next_y ] = player
        self.players[ player ].update( next_x, next_y )

        return 1

    def show( self ):
        pass

def main():
    b = Board( 10 ,1 ,2 ,1 )

if ( __name__ == '__main__' ):
    main()
