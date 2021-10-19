import curses
from curses import textpad
import socket
from board import Board
from client_protocol import Protocol_client
from enums import Squares as sq

N = 20
FPS = 60.0
N_BUTTONS = 3

strPlayer = {'1' : sq.P1, '2' : sq.P2 }

class Game:
    def __init__( self, port ):
        self.running = True

        self.start_game = False
        self.ip = socket.gethostbyname( socket.gethostname() )
        self.port = port
        self.addr = ( self.ip, self.port )
        self.conn = socket.socket()
        self.player = sq.EMPTY

    def assign_player( self, msg ):
        self.player = strPlayer[ msg[0] ]

    def set_game( self ):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def menu_window( self, screen ):
        self.set_game()

        k = 0
        height, width = screen.getmaxyx()

        start_y_first_button = int(height // 12)

        cursor_x = (width // 2) - ( 1 - (width % 2) )
        cursor_y = 0

        first_start_y = 9

        while ( k != ord('\n') ):

            # Initialization
            screen.clear()

            if k == curses.KEY_DOWN:
                cursor_y = cursor_y + 5
            elif k == curses.KEY_UP:
                cursor_y = cursor_y - 5

            cursor_x = max(0, cursor_x)
            cursor_x = min(width-1, cursor_x)

            cursor_y = max(first_start_y, cursor_y)
            cursor_y = min(first_start_y + ( ( N_BUTTONS - 1 ) * 5 ), cursor_y)

            choicebutton = []

            for i in range(N_BUTTONS):
                if ( i == ( ( cursor_y - first_start_y ) / 5 ) ):
                    choicebutton.append("X")
                else:
                    choicebutton.append(" ")


            # Declaration of strings
            title = "[TRON]"[:width-1]
            subtitle = "Feito por PBPJ, Ganso e Pinkuschu"[:width-1]
            statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)

            button = []
            button.append( "Conectar ao Jogo"[:width-1] )
            button.append( "Button TWO but bigger than ONE"[:width-1] )
            button.append( "Button THREE but ... different"[:width-1] )


            # Getting the max len between all buttons
            max_len_of_button = 0
            for butt in button:
                max_len_of_button = max ( max_len_of_button, len(butt) )

            for i in range( len(button) ):
                spacestr = ( (max_len_of_button - len(button[i]) + 1) // 2 ) * " "
                button_size = 3 + 2*len( spacestr ) + len( button[i] )


            # Centering calculations
            start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
            start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)

            start_y = int((height // 5) - 2)

            start_x_text = []

            for i in range(N_BUTTONS):
                start_x_text.append( int((width // 2) - (len(button[i]) // 2) - (len(button[i]) % 2)) )

            start_x_button = int((width // 2) - (max_len_of_button // 2) - (max_len_of_button % 2)) - 2

            # Rndering some text
            whstr = "Width: {}, Height: {}".format(width, height)
            screen.addstr(0, 0, whstr, curses.color_pair(1))

            # Render status bar
            screen.attron(curses.color_pair(3))
            screen.addstr(height-1, 0, statusbarstr)
            screen.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
            screen.attroff(curses.color_pair(3))

            # Turning on attributes for title
            screen.attron(curses.color_pair(2))
            screen.attron(curses.A_BOLD)

            # Rendering title
            screen.addstr(start_y, start_x_title, title)

            # Turning off attributes for title
            screen.attroff(curses.color_pair(2))
            screen.attroff(curses.A_BOLD)

            # Print rest of text
            screen.addstr(start_y + 1, start_x_subtitle, subtitle)

            for i in range( len(button) ):
                textpad.rectangle(screen, start_y_first_button + 5 + (i*5), start_x_button ,
                start_y_first_button + 5 + (i*5) + 3, start_x_button + button_size )

                if choicebutton[i] == "X":
                    screen.attron(curses.color_pair(3))
                screen.addstr( start_y_first_button + 5 + (i*5) + 1, start_x_text[i], button[i] )
                screen.addstr( start_y_first_button + 5 + (i*5) + 2, (width // 2) - ( 1 - (width % 2) ) - 1,
                             ( "[" + choicebutton[i] + "]") )
                if choicebutton[i] == "X":
                    screen.attroff(curses.color_pair(3))

            screen.move(cursor_y, cursor_x)

            #Refresh the screen
            screen.refresh()

            # Wait for next input
            k = screen.getch()

        screen.clear()
        screen.refresh()

        index = ( cursor_y - first_start_y ) / 5
        return index

    def waiting_window( self, screen ):
        self.conn.connect( self.addr )

        screen.nodelay( True )
        k = 0
        ready = False

        height, width = screen.getmaxyx()
        waitstr = "Aguardando o 2o Jogador se Conectar..."
        exitqstr = "Pressione 'q' para cancelar a CONEXAO"

        start_x_wait = int((width // 2) - (len(waitstr) // 2) - (len(waitstr) % 2)) - 2
        start_x_exit = int((width // 2) - (len(exitqstr) // 2) - (len(exitqstr) % 2)) - 2

        while ( not ready and k != ord('q') ):
            screen.clear()
            textpad.rectangle(screen, height // 2 - 1, start_x_wait-1, height // 2 + 1, start_x_wait + len(waitstr) )

            screen.addstr( height // 2, start_x_wait, waitstr )
            screen.addstr( 2*height // 3, start_x_exit, exitqstr )

            k = screen.getch()
            screen.refresh()

            msg = self.conn.recv( 4 )
            msg = msg.decode( 'utf-8' )

            if(len(msg) != 0):
                screen.clear()
                textpad.rectangle(screen, height // 2 - 1, start_x_wait-1, height // 2 + 1, start_x_wait + len(waitstr) )
                screen.addstr( height // 2, start_x_wait + 10, "Jogadores conectados" )
                screen.addstr( 2*height // 3, start_x_exit + 15, "Prepare-se" )
                screen.refresh()
                curses.napms(5000)
                self.assign_player( msg )
                ready = True

        return 0

    def game_window( self, screen ):
        board = Board( N )

        self.set_game()
        screen.clear()
        self.render( screen )
        screen.refresh()

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
        self.waiting()
        self.start()

    def menu( self ):
        curses.wrapper( self.menu_window )

    def waiting( self ):
        curses.wrapper( self.waiting_window )

    def start( self ):
        curses.wrapper( self.game_window )
