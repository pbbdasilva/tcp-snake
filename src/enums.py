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

class ChangeVolume(Enum):
    DECREASE = 0
    INCREASE = 1
    MUTE = 2
    DESMUTE = 3

class PlayerCaracters(Enum):
    OP1 = '*'
    OP2 = '^'
    OP3 = '~'
    OP4 = '+'