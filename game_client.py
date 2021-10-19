from board import Board
from client_protocol import Protocol_client
from curses import textpad
from enums import Squares as sq
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
        self.player = sq.EMPTY

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
        self.render( screen, board )

        key_pressed = 0
        server_input = Protocol_client()

        while( not server_input.end_game ):
            acc = 0.0

    def render( self, screen, board ):
        curses.curs_set(0)

        sh, sw = screen.getmaxyx()
        
        N = len(board)
        
        box = [[3,3],[sh-3,sw-3]]

        textpad.rectangle(screen, box[0][0],box[0][1],box[1][0], box[1][1])
        
        y_start,x_start  = sh//2-N//2,sw//2-(2*N-1)//2
        y,x = y_start,x_start
        
        for line in board:
            
            for element in line:
                if element == sq.EMPTY:
                    screen.addch(y,x,element.value, curses.color_pair(1))
                elif element == sq.P1:
                    screen.addch(y,x,element.value, curses.color_pair(2))
                elif element == sq.P2:
                    screen.addch(y,x,element.value, curses.color_pair(3)) 
                
                x = x+2
            
            x = x_start
            y = y+1
        
        screen.refresh()
        screen.getch()
    
    def update_screen(self,screen):
        pass

    def run( self ):
        self.menu()
        self.start()

    def menu( self ):
        curses.wrapper( self.menu_window )

    def start( self ):
        self.set_game()
        curses.wrapper( self.game_window )

