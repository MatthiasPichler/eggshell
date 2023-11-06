#! /usr/bin/env python3
import argparse
import sys
from eggshell.eggshell import Eggshell


def main():
    parser = argparse.ArgumentParser(prog="ai", description="Bring GTP to your CLI")

    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument("--forget", action="store_true", help="Clear the session")
    group.add_argument(
        "prompt",
        type=str,
        nargs="?",
        help="The prompt to generate a command for",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times)",
    )

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
