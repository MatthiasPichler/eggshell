import os
import sys
import eggshell.generate as generate
import eggshell.recordings as recordings
import eggshell.sessions as sessions
from eggshell.log import logger
import questionary
import subprocess


def eggshell(args):
    current_pid = os.getpid()
    ancestor_pids = recordings.get_ancestor_pids(current_pid)

    recording_path = recordings.find_recording(ancestor_pids)

    if not recording_path:
        return

    if args.clear:
        sessions.forget_session(recording_path)
        return

    session = sessions.get_session(recording_path)
    prompt = " ".join(sys.argv[1:])
    generated_command = generate.generate_next(
        prompt=prompt, recording="\n".join(session["lines"]) if session else ""
    )

    logger.debug(f"Generated command: {generated_command}")

    if isinstance(generated_command, generate.ExplainFunctionCall):
        print(generated_command.args.explanation)
    elif isinstance(generated_command, generate.SuggestCommandFunctionCall):
        command = generated_command.args.command
        if questionary.confirm(f"execute: {command}").ask():
            subprocess.run(f"exec {command}", shell=True)
