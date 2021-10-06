class Player:
    def __init__( self, addr, init_x, init_y, color ):
        self.color = color
        self.addr = addr
        self.x = init_x
        self.y = init_y

    def update( self, nxt_x, nxt_y ):
        self.x = nxt_x
        self.y = nxt_y