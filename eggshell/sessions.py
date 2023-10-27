import os
import json
import eggshell.recordings as recordings
import eggshell.config as config


def session_path(pid):
    return os.path.join(config.eggshell_path, ".recordings", f".session_{pid}")


def get_session(recording_path):
    pid = recordings.pid_from_recording(recording_path)
    if not pid:
        return None

    if not os.path.exists(session_path(pid)):
        with open(session_path(pid), "w") as session_file:
            session_file.write(json.dumps({"anchor": 0}))

    with open(session_path(pid), "r") as session_file:
        session_data = json.load(session_file)

    recording = recordings.get_recording(recording_path)
    if not recording:
        return None

    recording_lines = recording.split("\n")

    return {
        "anchor": session_data["anchor"],
        "lines": recording_lines[session_data["anchor"] :],
    }


def forget_session(recording_path):
    pid = recordings.pid_from_recording(recording_path)
    if not pid:
        return

    session_path = os.path.join(config.eggshell_path, ".recordings", f".session_{pid}")

    if not os.path.exists(session_path):
        with open(session_path, "w") as session_file:
            session_file.write(json.dumps({"anchor": 0}))

    session_file = open(session_path, "r")
    session_data = json.load(session_file)
    session_file.close()

    recording = open(recording_path, "r")
    recording_lines = recording.read().split("\n")
    recording.close()

    session_data["anchor"] = len(recording_lines)

    with open(session_path, "w") as session_file:
        session_file.write(json.dumps(session_data))
