from board import Board
N = 20

class Game:
    def __init__( self, addr1, addr2 ):
        self.running = True
        self.b = Board( N, addr1, addr2 )

    def run( self ):
        self.b.init_board()

        while ( self.running ):
            self.process_input()
            self.update()
            self.render()

    def process_input( self ):
        pass

    def update( self ):
        pass

    def render ( self ):
        pass