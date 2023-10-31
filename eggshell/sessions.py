import os
import json
from typing import Any
import eggshell.recordings as recordings
import eggshell.config as config


class Session:
    pid: int
    session_data: dict[str, Any]
    recording: recordings.Recording

    @property
    def path(self):
        return config.eggshell_session

    def __init__(self):
        self.pid = os.getpid()

        if not os.path.exists(self.path):
            with open(self.path, "w") as session_file:
                session_file.write(json.dumps({"offset": 0}))

        with open(self.path, "r") as session_file:
            self.session_data = json.load(session_file)

        self.recording = recordings.Recording(
            pid=self.pid, offset=self.session_data["offset"]
        )

    def forget(self):
        if not os.path.exists(self.path):
            with open(self.path, "w") as session_file:
                session_file.write(json.dumps({"offset": 0}))

        session_data = None
        with open(self.path, "r") as session_file:
            session_data = json.load(session_file)

        session_data["offset"] = len(self.recording.raw_recording_lines)

        with open(self.path, "w") as session_file:
            session_file.write(json.dumps(session_data))

        self.session_data = session_data
        self.recording.offset = session_data["offset"]
