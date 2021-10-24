import curses
from curses import textpad
import socket
import threading
import time
import sys
import random
import fonts
from board import Board
from audio_system import Background_music
from client_protocol import Protocol_client
from enums import Squares as sq
from enums import Directions as dir

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

            start_y_first_button = start_y + 3

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

    def write_win_lose_text( self, screen , winOrLose):
        
        width   = screen.getmaxyx()[1]
        half_height  = screen.getmaxyx()[0] // 2
        
        if ( winOrLose == 0 ):
            if ( width >= len( fonts.victory_text_big[0] ) ):
                text = fonts.victory_text_big
                print("VEIO NO BIG")
            else:
                text = fonts.victory_text_small
                print("VEIO NO SMALL")
        else:
            text = fonts.defeat_text
            print("VEIO NO DEFEAT")

        for i in range(len( text )):
            print("i = ", i, "- text[i] = ", text[i])
            try:
                screen.addstr(  half_height - ( len( text ) // 2 ) + i,
                                (width // 2) - (len(text[i]) // 2),
                                text[i],
                                curses.color_pair( 1 )  )
            except curses.error:
                pass

    def fire_column( self, screen ):
        screen  = curses.initscr()
        width   = screen.getmaxyx()[1]
        half_height  = screen.getmaxyx()[0] // 2
        size    = width * half_height
        char    = [" ", ".", ":", "^", "*", "x", "s", "S", "#", "$"]

        frontal_fire = []

        curses.init_pair(5, 0, 0)       # cor da "sombrinha"
        curses.init_pair(6, curses.COLOR_RED, 0)       # cor do fogo mais externo
        curses.init_pair(7, curses.COLOR_YELLOW, 0)       # cor do fogo intermediario
        curses.init_pair(8, curses.COLOR_BLUE, 0)       # cor do fogo mais interno

        screen.clear()
        
        for i in range(size+width+1): frontal_fire.append(0)

        while True:
            for i in range(int(width/9)): frontal_fire[int((random.random()*width)+width*(half_height-1))]=65
            for i in range(size):
                frontal_fire[i]=int((frontal_fire[i]+frontal_fire[i+1]+frontal_fire[i+width]+frontal_fire[i+width+1])/4)
                color=(4 if frontal_fire[i]>15 else (3 if frontal_fire[i]>9 else (2 if frontal_fire[i]>4 else 1)))
                if(i<size-1):   
                    screen.addstr(  int(half_height - i/width),           # top fire
                                    i%width,
                                    char[(9 if frontal_fire[i]>9 else frontal_fire[i])],
                                    curses.color_pair( color + 4 ) | curses.A_BOLD )

                #    screen.addstr(  half_height,
                #                    (width // 2) - (len(victory_text) // 2),
                #                    victory_text,
                #                    curses.color_pair( 1 ) )
                    
                #   textpad.rectangle(  screen, half_height - 3,
                #                    ( width // 2 ) - len(victory_text) - 1, 
                #                        half_height + 3, 
                #                        ( width // 2 ) + len(victory_text) + 1 )
                    
                    screen.addstr(  half_height + int(i/width),           # bottom fire
                                    i%width,
                                    char[(9 if frontal_fire[i]>9 else frontal_fire[i])],
                                    curses.color_pair( color + 4 ) | curses.A_BOLD )
            
            self.write_win_lose_text( screen, 0 )
            
            screen.refresh()
            screen.timeout(30)
            if (screen.getch()!=-1): break

    def winner_window( self, screen ):
        self.set_game()
        screen.clear()
        # screen.addstr(20, 20, "victory!!! :)")
        screen.refresh()

        self.fire_column( screen )
        # print "Pressione qualquer tecla para finalizar"
        k = screen.getch()

        return 0

    def snowing( self ):

        snowflakes = {
            '*': 1,
            '+': 0.8,
            '.': 0.4,
        }

        def max_dimensions(window):
            height, width = window.getmaxyx()
            return height - 2, width - 1

        def snowflake_char(window):
            width = max_dimensions(window)[1]
            char = random.choice(list(snowflakes.keys()))
            position = random.randrange(1, width)
            return (0, position, char)

        def update_snowflakes(prev, window):
            new = {}
            for (height, position), char in prev.items():
                max_height = max_dimensions(window)[0]
                new_height = height
                if random.random() <= snowflakes[char]:
                    new_height += 1
                    if new_height > max_height or prev.get((new_height, position)):
                        new_height -= 1
                new[(new_height, position)] = char
            return new

        def redisplay(snowflakes, window):
            for (height, position), char in snowflakes.items():
                max_height, max_width = max_dimensions(window)
                if height > max_height or position >= max_width:
                    continue
                window.addch(height, position, char)

        def draw_moon(window):
            moon = [
                '  **   ',
                '   *** ',
                '    ***',
                '    ***',
                '   *** ',
                '  **   ',
            ]
            start_position = max_dimensions(window)[1] - 10
            window.attrset(curses.color_pair(1))
            for height, line in enumerate(moon, start=1):
                for position, sym in enumerate(line, start=start_position):
                    window.addch(height, position, sym)
            window.attrset(curses.color_pair(0))

        def snowing_main(window, speed):
            if curses.can_change_color():
                curses.init_color(curses.COLOR_BLACK, 0,0,0)
                curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
                curses.init_color(curses.COLOR_YELLOW, 1000, 1000, 0)
            curses.init_pair(1, curses.COLOR_YELLOW, 0)
            try:
                curses.curs_set(0)
            except Exception:
                pass  # Can't hide cursor in 2019 huh?
            snowflakes = {}
            while True:
                height, width = max_dimensions(window)
                if len(snowflakes.keys()) >= 0.95 * (height * width):
                    snowflakes.clear()
                snowflakes = update_snowflakes(snowflakes, window)
                snowflake = snowflake_char(window)
                snowflakes[(snowflake[0], snowflake[1])] = snowflake[2]
                window.clear()
                redisplay(snowflakes, window)
                draw_moon(window)

                # Write the "Defeat" text
                self.write_win_lose_text( window, 1 )

                window.refresh()
                window.timeout(30)
                if (window.getch()!=-1): break
                try:
                    time.sleep((0.2) / (speed / 100))
                except ZeroDivisionError:
                    time.sleep(0.2)

        speed = 200
        curses.wrapper(snowing_main, speed)


    def loser_window( self, screen ):
        self.set_game()
        screen.clear()
        screen.addstr(20, 20, "lost ;(")
        screen.refresh()

        self.snowing()

        screen.getch()
        # curses.napms( 2000 )

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
