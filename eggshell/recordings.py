import psutil
import os
from ansicolors import strip_color
import eggshell.config as config


def get_parent_pid(pid):
    try:
        process = psutil.Process(pid)
        parent = process.parent()
        return parent.pid if parent else None
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None


def get_ancestor_pids(pid):
    ancestor_pids = []
    try:
        while pid is not None:
            ancestor_pids.append(pid)
            pid = get_parent_pid(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass  # Handle exceptions if needed

    return ancestor_pids


def recording_path(pid):
    return os.path.join(config.eggshell_path, ".recordings", f".recording_{pid}.txt")


def find_recording(pids):
    for pid in pids:
        if os.path.exists(recording_path(pid)):
            return recording_path(pid)
    return None


def pid_from_recording(recording):
    parts = recording.split("/")
    filename = parts[-1]
    pid = filename.split(".")[0] if "." in filename else None
    return pid


def get_recording(file_path):
    try:
        with open(file_path, "r") as file:
            file_contents = file.read()
            cleaned_contents = strip_color(file_contents)
            return cleaned_contents
    except Exception as e:
        print(f"Error reading and processing the file: {e}")
        return None
