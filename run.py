
from argparse import ArgumentParser, HelpFormatter
from server import create_server

def main():
    def formatter(prog):
        return HelpFormatter(prog, max_help_position=40)

    parser = ArgumentParser(description='Natural selection simulation', formatter_class=formatter)

    parser.add_argument('-s', '--seed', metavar='S', default=None,
        help='seed for the random number generator')
    parser.add_argument('--width', metavar='W', type=int, default=20,
        help='width of the grid world')
    parser.add_argument('--height', metavar='H', type=int, default=20,
        help='height of the grid world')
    parser.add_argument('-f', '--food-per-generation', metavar='F', type=int, default=60,
        help='amount of food per generation')
    parser.add_argument('-n', '--num-organisms', metavar='N', type=int, default=25,
        help='starting number of organisms')

    parser.add_argument('-ms', '--speed-mutation-rate', metavar='S', type=float, default=0.08,
        help='chance that a speed mutation will occur on replication')
    parser.add_argument('-ma', '--awareness-mutation-rate', metavar='A', type=float, default=0.08,
        help='chance that an awareness mutation will occur on replication')
    parser.add_argument('-mz', '--size-mutation-rate', metavar='S', type=float, default=0.08,
        help='chance that a size mutation will occur on replication')

    parser.add_argument('-is', '--initial-speed', metavar='S', type=int, default=3,
        help='speed of initial population')
    parser.add_argument('-ia', '--initial-awareness', metavar='A', type=int, default=2,
        help='awareness of initial population')
    parser.add_argument('-iz', '--initial-size', metavar='S', type=float, default=1.0,
        help='size of initial population')
    parser.add_argument('-it', '--initial-trail', metavar='T', type=float, default=0.5,
        help='percentage of initial population with trail gene')

    args = vars(parser.parse_args())
    server = create_server(args)
    server.launch()

if __name__ == '__main__':
    main()
