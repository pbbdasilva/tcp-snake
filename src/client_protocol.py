from enums import Squares as sq

playerStr = { sq.P1 : '1', sq.P2 : '2' }
strPlayer = {'1' : sq.P1, '2' : sq.P2 }

class Protocol_client:
    def __init__( self, destination = sq.EMPTY, direction = -1, end_game = False, who = sq.EMPTY ):
        self.direction = direction
        self.end_game = end_game
        self.who = who
        self.destination = destination

    def update( self, protocol ):
        self.direction = int( protocol[1] )
        self.end_game = ( protocol[2] == '1' )

        self.who = strPlayer[ protocol[3] ]
        self.destination = strPlayer[ protocol[0] ]

    def __str__( self ):
        protocol_msg = str( self.direction )

        protocol_msg += playerStr[ self.who ]

        if(self.end_game): protocol_msg += '1'
        else: protocol_msg += '0'

        return protocol_msg

