import os
from typing import Tuple
from colors import strip_color
import eggshell.config as config


class Recording:
    byte_offset: int
    # TODO: This should be configurable and selected better
    max_chars: int = 100_000

    @property
    def path(self):
        return config.eggshell_recording

    @property
    def _raw_recording_lines(self):
        with open(self.path, "r") as file:
            return file.readlines()

    @property
    def _raw_recording(self):
        with open(self.path, "r") as file:
            return file.read()

    def read_recording(self) -> Tuple[str, int]:
        with open(self.path, "r") as file:
            file.seek(self.byte_offset)
            raw_content = file.read()
            cleaned_content = strip_color(raw_content)
            trimmed_content = cleaned_content[-self.max_chars :]
            file.seek(0, os.SEEK_END)
            self.byte_offset = file.tell()
            return (trimmed_content, self.byte_offset)

    def __init__(self, byte_offset: int):
        self.byte_offset = byte_offset

    def __str__(self):
        return f"Recording(path={self.path}, byte_offset={self.byte_offset}, max_chars={self.max_chars})"

    def __repr__(self):
        return str(self)
