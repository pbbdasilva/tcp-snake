import curses
from curses import textpad
import socket
import threading
import time
import sys
from board import Board
from audio_system import Background_music
from client_protocol import Protocol_client
from enums import Squares as sq
from enums import Directions as dir
from visual_effects.snow_screen import display_snow
from visual_effects.fire_screen import display_fire


N = 20
FPS = 60.0
N_BUTTONS = 3
PROTOCOL_SIZE = 4

strDir = { '0' : dir.RIGHT, '1' : dir.UP, '2' : dir.LEFT, '3' : dir.DOWN }
dirStr = { dir.RIGHT : '0', dir.UP : '1', dir.LEFT : '2', dir.DOWN : '3' }

strPlayer = { '1' : sq.P1, '2' : sq.P2 }
playerStr = { sq.P1 : '1', sq.P2 : '2' }

class Game:
    def __init__( self, port ):
        self.running = True
        self.loser = sq.EMPTY

        self.ip = socket.gethostbyname( socket.gethostname() )
        self.port = port
        self.addr = ( self.ip, self.port )
        self.conn = socket.socket()

        self.player = sq.EMPTY
        self.lock = threading.Lock()

        self.screen_idx = 0
        self.screens = [ self.menu, self.waiting, self.settings, self.quit, self.start, self.end ]
        self.back_music = Background_music()

    def send_move( self, move_direction ):
        protocol = Protocol_client( destination=self.player, direction=int( dirStr[ move_direction ] ), who=self.player )
        protocol_msg = playerStr[ self.player ] + str( protocol )

        self.lock.acquire()
        self.conn.send( protocol_msg.encode('utf-8') )
        self.lock.release()

    def process_input( self, msg ):
        dir_idx = strDir[ msg[1] ]
        who_moved = strPlayer[ msg[2] ]

        end_game = True
        game_status = self.b.move( who_moved, dir_idx )
        if( game_status == 1 ):
            end_game = False

        self.running = not end_game
        if( end_game ): self.loser = who_moved

    def handle_input( self ):
        while( self.running ):
            bytes_received = 0
            server_msg = ""

            while( bytes_received < PROTOCOL_SIZE ):
                tmp_msg = self.conn.recv( PROTOCOL_SIZE )
                tmp_msg = tmp_msg.decode('utf-8')
                bytes_received += len(tmp_msg)
                server_msg += tmp_msg

            self.process_input( server_msg )

    def assign_player( self, msg ):
        self.player = strPlayer[ msg[0] ]

    def set_game( self ):
        curses.start_color()
        curses.curs_set( 0 )
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4,curses.COLOR_GREEN,curses.COLOR_BLACK)

    def menu_window( self, screen ):
        self.set_game()
        self.back_music.play(0)

        screen.nodelay( False )

        k = 0
        height, width = screen.getmaxyx()

        # start_y_first_button = int(height // 12) !
        cursor_x = (width // 2) - ( 1 - (width % 2) )
        cursor_y = 0

        first_start_y = 9

        while ( k != ord('\n') ):
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
            button.append( "Configurações"[:width-1] )
            button.append( "Sair"[:width-1] )


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

            # start_y_first_button = start_y + 3 !
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
                textpad.rectangle(screen, start_y_first_button + (i*5), start_x_button ,
                start_y_first_button + (i*5) + 3, start_x_button + button_size )

                if choicebutton[i] == "X":
                    screen.attron(curses.color_pair(3))
                screen.addstr( start_y_first_button + (i*5) + 1, start_x_text[i], button[i] )
                screen.addstr( start_y_first_button + (i*5) + 2, (width // 2) - ( 1 - (width % 2) ) - 1,
#                 textpad.rectangle(screen, start_y_first_button + 5 + (i*5), start_x_button ,
#                 start_y_first_button + 5 + (i*5) + 3, start_x_button + button_size )

#                 if choicebutton[i] == "X":
#                     screen.attron(curses.color_pair(3))
#                 screen.addstr( start_y_first_button + 5 + (i*5) + 1, start_x_text[i], button[i] )
#                 screen.addstr( start_y_first_button + 5 + (i*5) + 2, (width // 2) - ( 1 - (width % 2) ) - 1,
                             ( "[" + choicebutton[i] + "]") )
                if choicebutton[i] == "X":
                    screen.attroff(curses.color_pair(3))

            screen.move(cursor_y, cursor_x)
            screen.refresh()

            k = screen.getch()

        screen.clear()
        screen.refresh()

        index = ( cursor_y - first_start_y ) / 5
        return int( index ) + 1

    def waiting_window( self, screen ):
        self.back_music.play(1)
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

        return 4

    def game_window( self, screen ):
        self.b = Board( N )

        self.set_game()
        screen.keypad( True )
        screen.nodelay( True )
        self.render( screen )

        key_pressed = 0
        thread = threading.Thread(target=self.handle_input)
        thread.name = "server_io"
        thread.start()

        acc = 0.0
        while( self.running ):
            t1 = time.time()
            key_pressed = screen.getch()

            if( key_pressed == -1 ):
                pass
            elif(key_pressed == curses.KEY_UP):
                screen.addch(1, 0, '^')
                self.send_move( dir.UP )
            elif(key_pressed == curses.KEY_RIGHT):
                screen.addch(1, 0, '>')
                self.send_move( dir.RIGHT )
            elif(key_pressed == curses.KEY_LEFT):
                screen.addch(1, 0, '<')
                self.send_move( dir.LEFT )
            elif(key_pressed == curses.KEY_DOWN):
                screen.addch(1, 0, 'v')
                self.send_move( dir.DOWN )

            dt = time.time() - t1
            acc += dt

            if( acc >= 1/FPS ):
                self.render( screen )
                acc = 0.0

        return 5

    def winner_window( self, screen ):
        display_fire( screen )
        return 0

    def loser_window( self, screen ):
        display_snow( screen )
        return 0

    def settings_window( self, screen ):
        self.set_game()
        screen.clear()
        screen.addstr(20, 20, "In the future you will adjust your settings here...")
        screen.refresh()
        curses.napms( 2000 )

        return 0

    def quit_window( self, screen ):
        self.set_game()
        screen.clear()
        screen.addstr(20, 20, "bye :)")
        screen.refresh()
        curses.napms( 2000 )

    def render( self, screen ):
        t1 = time.time()
        screen.clear()

        sh, sw = screen.getmaxyx()
        box = [ [ 3, 3 ], [ sh - 3, sw - 3 ] ]

        textpad.rectangle( screen, box[0][0], box[0][1], box[1][0], box[1][1] )

        y_start, x_start  = sh // 2 - N // 2, sw // 2 - (2*N-1) // 2
        y, x = y_start, x_start

        for line in self.b.board:
            for element in line:
                if element == sq.EMPTY:
                    screen.addch(y,x,element.value, curses.color_pair(1))
                elif element == sq.P1:
                    screen.addch(y,x,element.value, curses.color_pair(2))
                elif element == sq.P2:
                    screen.addch(y,x,element.value, curses.color_pair(4))

                x += 2

            x = x_start
            y += 1
        dt = time.time() - t1
        screen.addstr(0, 0, str(dt))
        screen.refresh()

    def run( self ):
        while( True ):
            next_idx = self.screens[ self.screen_idx ]()
            self.screen_idx = next_idx

    def menu( self ):
        return curses.wrapper( self.menu_window )

    def waiting( self ):
        return curses.wrapper( self.waiting_window )

    def start( self ):
        return curses.wrapper( self.game_window )

    def end( self ):
        self.conn.close()
        if( self.loser == self.player ):
            return curses.wrapper( self.loser_window )
        else:
            return curses.wrapper( self.winner_window )

    def quit( self ):
        curses.wrapper( self.quit_window )
        sys.exit()

    def settings( self ):
        return curses.wrapper( self.settings_window )

def main():
    g = Game(5050)
    g.start()

if __name__ == '__main__':
    main()
