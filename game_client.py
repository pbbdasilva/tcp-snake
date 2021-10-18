from board import Board
from game_client import Protocol_client
from enums import Squares as sq
import curses
import socket

N = 20
FPS = 60.0
N_BUTTONS = 3

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
        
        k = 0
        height, width = screen.getmaxyx()

        start_y_first_button = int(height // 12)

        cursor_x = (width // 2) - ( 1 - (width % 2) )
        cursor_y = 0

        first_start_y = 9

        while (k != ord('q')):

            # Initialization
            screen.clear()

            if k == curses.KEY_DOWN:
                cursor_y = cursor_y + 5
            elif k == curses.KEY_UP:
                cursor_y = cursor_y - 5
            elif k == curses.KEY_ENTER or k == ord('\n'):
                break

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
            keystr = "Last key pressed: {}".format(k)[:width-1]
            statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)
            if k == 0:
                keystr = "No key press detected..."[:width-1]

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

            choicestr = ( (button_size // 2) - (button_size % 2) - 1 ) * " "

            for i in range( len(button) ):
                curses.textpad.rectangle(screen, start_y_first_button + 5 + (i*5), start_x_button , 
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

        if ( k == curses.KEY_ENTER or k == ord('\n') ):
            index = ( cursor_y - first_start_y ) / 5
            if index == 0:
                screen.addstr( 0, 0, "1a Opcao Selecionada")
            elif index == 1:
                screen.addstr( 0, 0, "2a Opcao Selecionada")
            elif index == 2:
                screen.addstr( 0, 0, "3a Opcao Selecionada")

        screen.addstr( 1, 0, "Pressione qualquer tecla para sair..." )
        x = screen.getch()

        return 0

    def waiting_window( self, screen ):

        k = 0
        height, width = screen.getmaxyx()
        waitstr = "Aguardando o 2o Jogador se Conectar..."
        exitqstr = "Pressione 'q' para cancelar a CONEXAO"

        start_x_wait = int((width // 2) - (len(waitstr) // 2) - (len(waitstr) % 2)) - 2
        start_x_exit = int((width // 2) - (len(exitqstr) // 2) - (len(exitqstr) % 2)) - 2

        while (not self.conn_ready() and k != ord('q')):

            curses.textpad.rectangle(screen, height // 2 - 1, start_x_wait-1, height // 2 + 1, start_x_wait + len(waitstr) )

            screen.addstr( height // 2, start_x_wait, waitstr )
            screen.addstr( 2*height // 3, start_x_exit, exitqstr )

            k = screen.getch()

            screen.clear()
            screen.refresh()
        
        return 0

    def conn_ready( self ):
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
        self.waiting()
        self.start()

    def menu( self ):
        curses.wrapper( self.menu_window )

    def waiting( self ):
        curses.wrapper( self.waiting_window )

    def start( self ):
        self.set_game()
        curses.wrapper( self.game_window )