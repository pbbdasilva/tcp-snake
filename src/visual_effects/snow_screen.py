import curses
import random
import time
from visual_effects.ascii_fonts import Font

SNOW_SPEED = 200
SNOWFLAKES = { '*': 1, '+': 0.8, '.': 0.4 }

def display_message( screen ):
    fonts = Font()
    width   = screen.getmaxyx()[1]
    half_height  = screen.getmaxyx()[0] // 2
    text = fonts.defeat_text

    for i in range(len( text )):
        try:
            screen.addstr( half_height - ( len( text ) // 2 ) + i,
                           (width // 2) - (len(text[i]) // 2),
                           text[i],
                           curses.color_pair( 1 ) )
        except curses.error:
            pass

def set_colors():
    curses.init_color(curses.COLOR_BLACK, 0,0,0)
    curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
    curses.init_color(curses.COLOR_YELLOW, 1000, 1000, 0)
    curses.init_pair(1, curses.COLOR_YELLOW, 0)
    curses.curs_set(0)

def max_dimensions( screen ):
    height, width = screen.getmaxyx()

    return height - 2, width - 1

def snowflake_char( screen ):
    width = max_dimensions( screen )[1]
    char = random.choice( list(SNOWFLAKES.keys()) )
    position = random.randrange(1, width)

    return (0, position, char)

def update_snowflakes(prev, screen):
    new = {}
    for (height, position), char in prev.items():
        max_height = max_dimensions(screen)[0]
        new_height = height

        if( random.random() <= SNOWFLAKES[char] ):
            new_height += 1
            if( new_height > max_height or prev.get((new_height, position)) ):
                new_height -= 1

        new[(new_height, position)] = char

    return new

def redisplay(snowflakes, screen):
    for (height, position), char in snowflakes.items():
        max_height, max_width = max_dimensions(screen)
        if height > max_height or position >= max_width: continue
        screen.addch(height, position, char)

def display_snow( screen ):
    set_colors()
    snowflakes = {}

    while True:
        height, width = max_dimensions( screen )
        if( len(snowflakes.keys()) >= 0.95 * (height * width) ):
            snowflakes.clear()

        snowflakes = update_snowflakes(snowflakes, screen)
        snowflake = snowflake_char(screen)
        snowflakes[ (snowflake[0], snowflake[1]) ] = snowflake[2]
        screen.clear()
        redisplay(snowflakes, screen)
        # draw_moon(screen)

        display_message( screen )

        screen.refresh()
        screen.timeout(30)

        if (screen.getch()!=-1): break
        time.sleep((0.2) / (SNOW_SPEED / 100))

if __name__ == "__main__":
    curses.wrapper( display_snow )