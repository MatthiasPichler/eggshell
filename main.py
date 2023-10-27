import argparse
import eggshell.eggshell as eggshell


def main():
    parser = argparse.ArgumentParser(
        prog="Eggshell", description="Bring GTP to your CLI"
    )

    parser.add_argument("-c", "--clear", action="store_true", help="Clear the session")
    parser.add_argument("prompt", type=str, help="The prompt to generate a command for")

    args = parser.parse_args()

    eggshell.eggshell(args)


if __name__ == "__main__":
    main()
