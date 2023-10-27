import os
import sys
from eggshell import ai
import eggshell.recordings as recordings
import eggshell.sessions as sessions


def eggshell(args):
    current_pid = os.getpid()
    ancestor_pids = recordings.get_ancestor_pids(current_pid)

    recording_path = recordings.find_recording(ancestor_pids)

    if not recording_path:
        return

    if args["clear"]:
        sessions.forget_session(recording_path)
        return

    session = sessions.get_session(recording_path)
    prompt = " ".join(sys.argv[1:])
    generated_command = ai.generate_next(
        prompt=prompt, recording="\n".join(session["lines"]) if session else ""
    )

    if len(generated_command) > 120 and not generated_command.startswith("echo"):
        print(generated_command)
    else:
        write_text(generated_command)
