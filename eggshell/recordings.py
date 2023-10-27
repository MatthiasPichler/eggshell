import os
from colors import strip_color
import eggshell.config as config


class Recording:
    pid: int
    path: str
    offset: int

    @staticmethod
    def _recording_path(pid):
        return os.path.join(
            config.eggshell_path, ".recordings", f".recording_{pid}.txt"
        )

    @property
    def raw_recording_lines(self):
        with open(self.path, "r") as file:
            return file.readlines()

    @property
    def raw_recording(self):
        with open(self.path, "r") as file:
            return file.read()

    @property
    def recording(self):
        with open(self.path, "r") as file:
            file_contents = file.readlines()
            truncated_contents = file_contents[self.offset :]
            cleaned_contents = strip_color("\n".join(truncated_contents))
            return cleaned_contents

    def __init__(self, pid, offset):
        self.pid = pid
        self.offset = offset
        self.path = Recording._recording_path(pid)

    def __str__(self):
        return f"Recording(pid={self.pid}, path={self.path})"

    def __repr__(self):
        return str(self)
