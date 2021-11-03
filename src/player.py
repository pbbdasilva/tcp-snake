from enums import Directions as dir

class Player:
    def __init__( self, color, init_x, init_y, init_direction ):
        self.color = color
        self.x = init_x
        self.y = init_y
        self.direction = init_direction

    def update( self, nxt_x, nxt_y ):
        self.x = nxt_x
        self.y = nxt_y

    def set_direction( self, new_dir ):
        self.direction = new_dir

    def get_direction( self ):
        return self.direction

    def get_coord( self ):
        return self.x, self.y