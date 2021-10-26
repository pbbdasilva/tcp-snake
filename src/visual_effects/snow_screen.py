import curses
import random
import time
import fonts
import drawings

SNOW_SPEED = 200

def display_message( screen ):
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

def draw_moon( screen ):
    moon = drawings.moon
    start_position = max_dimensions(screen)[1] - 10
    screen.attrset(curses.color_pair(1))

    for height, line in enumerate(moon, start=1):
        for position, sym in enumerate(line, start=start_position):
            screen.addch(height, position, sym)

    screen.attrset(curses.color_pair(0))

def snowflake_char( screen ):
    width = max_dimensions( screen )[1]
    char = random.choice( list(drawings.snowflakes.keys()) )
    position = random.randrange(1, width)

    return (0, position, char)

def update_snowflakes(prev, screen):
    new = {}
    for (height, position), char in prev.items():
        max_height = max_dimensions(screen)[0]
        new_height = height

        if( random.random() <= drawings.snowflakes[char] ):
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

def display_screen( screen ):
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
    curses.wrapper( display_screen )