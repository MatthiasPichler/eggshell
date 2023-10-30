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

    generated_command = None

    try:
        generated_command = generate.generate_next(
            prompt=args.prompt, recording=session.recording.recording
        )
    except generate.OutputTruncated as e:
        logger.debug(e)
        print("The generated output was too long:")
        print(f"{e.message}...[truncated].")
        print("If the output is insufficient please try again.")
        return
    except generate.UnclearResponse as e:
        logger.debug(e)
        print("The AI was not able to generate a command:")
        print(e.message)
        print("Please try again.")
    except Exception as e:
        logger.error(e)
        exit(1)

    logger.debug(f"Generated command: {generated_command}")

    if isinstance(generated_command, generate.ExplainFunctionCall):
        print(generated_command.args.explanation)
    elif isinstance(generated_command, generate.SuggestCommandFunctionCall):
        command = generated_command.args.command
        if questionary.confirm(f"execute: {command}").ask():
            subprocess.run(f"exec {command}", shell=True)
