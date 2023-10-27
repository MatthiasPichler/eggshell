import os
import psutil
import json
from typing import Any
import eggshell.recordings as recordings
import eggshell.config as config
from eggshell.log import trace


class Session:
    pid: int
    session_data: dict[str, Any]
    recording: recordings.Recording

    @trace
    @staticmethod
    def _get_parent_pid(pid):
        try:
            process = psutil.Process(pid)
            parent = process.parent()
            return parent.pid if parent else None
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None

    @trace
    @staticmethod
    def _get_ancestor_pids(pid):
        ancestor_pids = []
        try:
            while pid is not None:
                ancestor_pids.append(pid)
                pid = Session._get_parent_pid(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Handle exceptions if needed

        return ancestor_pids

    @trace
    @staticmethod
    def _find_first_ancestor_process(pids):
        for pid in pids:
            recording_path = recordings.Recording._recording_path(pid)
            if os.path.exists(recording_path):
                return pid
        return None

    @trace
    @staticmethod
    def _session_path(pid):
        return os.path.join(config.eggshell_path, ".recordings", f".session_{pid}")

    def __init__(self):
        current_pid = os.getpid()
        ancestor_pids = Session._get_ancestor_pids(current_pid)

        ancestor = Session._find_first_ancestor_process(ancestor_pids)

        if not ancestor:
            raise Exception("No ancestor found.")

        self.pid = ancestor
        self.path = Session._session_path(ancestor)

        if not os.path.exists(self.path):
            with open(self.path, "w") as session_file:
                session_file.write(json.dumps({"offset": 0}))

        with open(self.path, "r") as session_file:
            self.session_data = json.load(session_file)

        self.recording = recordings.Recording(
            pid=ancestor, offset=self.session_data["offset"]
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
