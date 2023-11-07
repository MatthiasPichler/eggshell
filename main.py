#! /usr/bin/env python3
from eggshell.cli import parser
import sys
from eggshell.config import Config
from eggshell.eggshell import Eggshell


def main():
    args = parser.parse_args()

    if not sys.stdin.isatty():
        args.prompt = sys.stdin.read()
    else:
        print("How can I help:")
        args.prompt = sys.stdin.readline().strip()

    config = Config(args)

    eggshell = Eggshell(args=args, config=config)
    eggshell.run()


if __name__ == "__main__":
    main()
