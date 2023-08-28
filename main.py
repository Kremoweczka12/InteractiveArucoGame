import argparse

from aruco_game.aruco_game import ArucoGame

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-u', '--ufo', required=True, type=int, help="specify number of enemy ships")
    parser.add_argument('-c', '--coins', required=True, type=int, help="specify number of coins")
    parser.add_argument('-m', '--music', action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    ArucoGame(args.ufo, args.coins, args.music)
