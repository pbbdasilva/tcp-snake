from game_client import Game
import consts

def main():
    g = Game( consts.PORT )
    g.run()

if __name__ == '__main__':
    main()