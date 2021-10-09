from board import Board
from game_client import Protocol_client
import curses
import socket

N = 20
FPS = 60.0

class Game:
    def __init__( self, port ):
        self.running = True
        self.start_game = False
        self.ip = socket.gethostbyname( socket.gethostname() )
        self.port = port
        self.addr = ( self.ip, self.port )
        self.conn = socket.socket()

    def set_game( self, screen ):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def menu_window( self, screen ):
        pass

    def game_window( self, screen ):
        board = Board( N )

        self.set_game( screen )
        screen.clear()
        self.render( screen )

        key_pressed = 0
        server_input = Protocol_client()

        while( not server_input.end_game ):
            acc = 0.0

    def render( self, screen ):
        pass

    def run( self ):
        self.menu()
        self.start()

    def menu( self ):
        curses.wrapper( self.menu_window )

    def start( self ):
        self.set_game()
        curses.wrapper( self.game_window )