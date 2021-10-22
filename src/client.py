from game_client import Game

PORT = 5050

def main():
    g = Game( PORT )
    g.run()

if __name__ == '__main__':
    main()