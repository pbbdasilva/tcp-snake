class Player:
    def __init__( self, color, init_x, init_y ):
        self.color = color
        self.x = init_x
        self.y = init_y

    def update( self, nxt_x, nxt_y ):
        self.x = nxt_x
        self.y = nxt_y