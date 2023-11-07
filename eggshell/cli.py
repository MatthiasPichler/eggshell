import argparse
import os
from eggshell.config import defaults

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
    "--config",
    type=str,
    help="Path to the config file. Defaults to ~/.eggshell/config",
)

parser.add_argument(
    "--profile",
    type=str,
    help="The configuration profile to use",
)

parser.add_argument(
    "--model",
    type=str,
    help="The GPT model to use",
    default=defaults["model"],
    choices=["gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview"],
)

parser.add_argument(
    "--api-key",
    type=str,
    help="The OpenAI API key to use",
    default=os.environ.get("OPENAI_API_KEY"),
)

parser.add_argument(
    "--recording",
    type=str,
    help="The path to the recording file",
    default=os.environ.get("EGGSHELL_RECORDING"),
)

# TODO: remove when using to assistants API
parser.add_argument(
    "--session",
    type=str,
    help="The path to the session file",
    default=os.environ.get("EGGSHELL_SESSION"),
)

parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Increase verbosity (can be used multiple times)",
)
