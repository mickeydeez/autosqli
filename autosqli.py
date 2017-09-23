#!/usr/bin/python

from lib.fuzzer import Fuzzer
from lib.dbconnection import DatabaseSession
from argparse import ArgumentParser
from sys import exit

def run():
    args = parse_args()
    if args.loops:
        fuzz = Fuzzer(loops=args.loops)
    else:
        fuzz = Fuzzer()
    if args.scan:
        fuzz.run_scan()
    if args.read:
        DatabaseSession().read()

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-s',
        '--scan',
        action='store_const',
        const=True,
        dest='scan',
        help="Run a scan against the defined queries"
    )
    parser.add_argument(
        '-r',
        '--read',
        action='store_const',
        const=True,
        dest='read',
        help="Dump local target database"
    )
    parser.add_argument(
        '-l',
        '--loop',
        action='store',
        dest='loops',
        help="Number of scrapes to do. Default is 5"
    )
    args = parser.parse_args()
    if not args.scan and not args.read:
        parser.print_help()
        exit(1)
    return args


if __name__ == '__main__':
    run()
