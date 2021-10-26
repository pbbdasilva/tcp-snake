import curses
from random import random
import drawings
import fonts

def set_colors():
    curses.start_color()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4,curses.COLOR_GREEN,curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, 0)       # cor da "sombrinha"
    curses.init_pair(6, curses.COLOR_RED, 0)       # cor do fogo mais externo
    curses.init_pair(7, curses.COLOR_YELLOW, 0)       # cor do fogo intermediario
    curses.init_pair(8, curses.COLOR_BLUE, 0)       # cor do fogo mais interno

def fire_color( fire_intensity ):
    if( fire_intensity > 15 ): return 4
    elif( fire_intensity > 9 ): return 3
    elif( fire_intensity > 4 ): return 2

    return 1

def display_message( screen ):
    width   = screen.getmaxyx()[1]
    half_height  = screen.getmaxyx()[0] // 2
    text = fonts.victory_text_small

    for i in range(len( text )):
        try:
            screen.addstr( half_height - ( len( text ) // 2 ) + i,
                           (width // 2) - (len(text[i]) // 2),
                           text[i],
                           curses.color_pair( 1 ) )
        except curses.error:
            pass

def display_screen( screen ):
    set_colors()
    screen.clear()
    width   = screen.getmaxyx()[1]
    half_height  = screen.getmaxyx()[0] // 2
    size    = width * half_height

    frontal_fire = [ 0 for _ in range( size + width + 1 ) ]

    while True:
        for i in range( int(width / 9 ) ):
            frontal_fire[ int( ( random() * width ) + width * ( half_height - 1 ) ) ] = 65

        for i in range(size):
            frontal_fire[i]=int((frontal_fire[i]+frontal_fire[i+1]+frontal_fire[i+width]+frontal_fire[i+width+1])/4)
            color = fire_color( frontal_fire[i] )

            if( i < size-1 ):
                screen.addstr(  int(half_height - i/width), i%width, drawings.fire_particles[ min( 9, frontal_fire[i] ) ],
                                curses.color_pair( color + 4 ) | curses.A_BOLD )

                screen.addstr(  half_height + int(i/width), i%width, drawings.fire_particles[ min( 9, frontal_fire[i] ) ],
                                curses.color_pair( color + 4 ) | curses.A_BOLD )

        display_message( screen )

        screen.refresh()
        screen.timeout(30)

        if( screen.getch() != -1 ): break

if __name__ == "__main__":
    curses.wrapper( display_screen )