from game_server import Game

N_PLAYERS = 1
N_AIS = 1
def main():
    g = Game(N_PLAYERS, N_AIS)
    g.run()

if __name__ == '__main__':
    main()
