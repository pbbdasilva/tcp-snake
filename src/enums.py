from enum import Enum

class Squares(Enum):
    EMPTY = '-'
    P1 = '*'
    P2 = '^'

class Directions(Enum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3
