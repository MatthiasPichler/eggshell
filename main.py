#! /usr/bin/env python3
from eggshell.cli import parser
import sys
from eggshell.eggshell import Eggshell


def main():
    args = parser.parse_args()

    if not sys.stdin.isatty():
        args.prompt = sys.stdin.read()
    else:
        print("How can I help:")
        args.prompt = sys.stdin.readline().strip()

    eggshell = Eggshell(args)
    eggshell.run()


if __name__ == "__main__":
    main()
