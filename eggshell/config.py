import os

# TODO: This is a hacky way to get the eggshell path. We should probably set a default
eggshell_path = os.environ.get("EGGSHELL_PATH") or ""
