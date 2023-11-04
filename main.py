#! /usr/bin/env python3
import argparse
import eggshell.eggshell as eggshell


def main():
    parser = argparse.ArgumentParser(
        prog="Eggshell", description="Bring GTP to your CLI"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-c", "--clear", action="store_true", help="Clear the session")
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

    eggshell.eggshell(args)


if __name__ == "__main__":
    main()
