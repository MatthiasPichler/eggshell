from colors import strip_color
import eggshell.config as config


class Recording:
    pid: int
    offset: int
    # TODO: This should be configurable and selected better
    max_chars: int = 100_000

    @property
    def path(self):
        return config.eggshell_recording

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
        file_contents = self.raw_recording_lines
        truncated_contents = file_contents[self.offset :]
        cleaned_contents = strip_color("\n".join(truncated_contents))
        trimmed_contents = cleaned_contents[-self.max_chars :]
        return trimmed_contents

    def __init__(self, pid, offset):
        self.pid = pid
        self.offset = offset

    def __str__(self):
        return f"Recording(pid={self.pid}, path={self.path})"

    def __repr__(self):
        return str(self)
