
from argparse import ArgumentParser
from server import create_server

def main():
    parser = ArgumentParser(description='Natural selection simulation')

    parser.add_argument('--width', metavar='W', type=int, default=20,
        help='width of the grid world')
    parser.add_argument('--height', metavar='H', type=int, default=20,
        help='height of the grid world')
    parser.add_argument('-f', '--food-per-generation', metavar='F', type=int, default=60,
        help='amount of food per generation')
    parser.add_argument('-n', '--num-organisms', metavar='N', type=int, default=25,
        help='starting number of organisms')

    parser.add_argument('-ds', '--disable-speed', help='disable speed mutations', action='store_true')
    parser.add_argument('-da', '--disable-awareness', help='disable awareness mutations', action='store_true')
    parser.add_argument('-dz', '--disable-size', help='disable size mutations', action='store_true')

    parser.add_argument('-is', '--initial-speed', type=int, default=3,
        help='speed of initial population')
    parser.add_argument('-ia', '--initial-awareness', type=int, default=2,
        help='awareness of initial population')
    parser.add_argument('-iz', '--initial-size', type=float, default=1.0,
        help='size of initial population')
    parser.add_argument('-it', '--initial-trail', type=float, default=0.5,
        help='percentage of initial population with trail gene')

    args = vars(parser.parse_args())
    server = create_server(args)
    server.launch()

if __name__ == '__main__':
    main()
