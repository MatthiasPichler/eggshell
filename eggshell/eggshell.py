import eggshell.generate as generate
import eggshell.sessions as sessions
from eggshell.log import logger, trace
import questionary
import subprocess


@trace
def eggshell(args):
    if args.verbose == 1:
        logger.setLevel("INFO")
    elif args.verbose == 2:
        logger.setLevel("DEBUG")
    elif args.verbose >= 3:
        logger.setLevel("TRACE")

    session = sessions.Session()

    if args.clear:
        session.forget()
        return

    generated_command = generate.generate_next(
        prompt=args.prompt, recording=session.recording.recording
    )

    logger.debug(f"Generated command: {generated_command}")

    if isinstance(generated_command, generate.ExplainFunctionCall):
        print(generated_command.args.explanation)
    elif isinstance(generated_command, generate.SuggestCommandFunctionCall):
        command = generated_command.args.command
        if questionary.confirm(f"execute: {command}").ask():
            subprocess.run(f"exec {command}", shell=True)
