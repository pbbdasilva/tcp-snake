from enums import Squares as sq

class Protocol_client:
    def __init__( self, direction = -1, end_game = False, who = sq.EMPTY ):
        self.direction = direction
        self.end_game = end_game
        self.who = who

    def update( self, protocol ):
        self.direction = int( protocol[0] )
        self.end_game = ( protocol[1] == '1' )

        if( protocol[2] == '1' ):
            self.who = sq.P1
        else:
            self.who = sq.P2

    def __str__( self ):
        protocol_msg = str( self.direction )

        if(self.end_game): protocol_msg += '1'
        else: protocol_msg += '0'

        if(self.who == sq.P1): protocol_msg += '1'
        else: protocol_msg += '2'

        return protocol_msg

