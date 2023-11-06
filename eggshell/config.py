from argparse import Namespace
import configparser
import os
from typing import Any, Literal, Mapping

defaults: Mapping[Literal["model", "api_key"], str] = {
    "model": "gpt-4-1106-preview",
    "api_key": os.environ.get("OPENAI_API_KEY", ""),
}
_default_config_path = os.path.expanduser("~/.eggshell/config")
_parser_defaults: Any = defaults
parser = configparser.ConfigParser(default_section="default", defaults=_parser_defaults)


class Config:
    path: str
    profile: str
    model: Literal["gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview"]
    api_key: str
    recording_file_path: str
    # TODO: remove when using to assistants API
    session_db_path: str

    def __init__(self, args: Namespace):
        self.path = _default_config_path
        self.model = args.model
        self.api_key = args.api_key
        self.recording_file_path = args.recording
        self.session_db_path = args.session
        self.profile = parser.default_section

        if args.config and not os.path.exists(args.config):
            raise Exception(f"Config file not found at {args.config}")

        if args.config:
            self.path = args.config
        elif not os.path.exists(_default_config_path):
            os.makedirs(os.path.dirname(_default_config_path), exist_ok=True)
            with open(_default_config_path, "w") as f:
                parser.write(f)

        parser.read(self.path)

        if args.profile and args.profile not in parser:
            raise Exception(
                f"Profile {args.profile} not found in config file at {self.path}"
            )

        if args.profile:
            self.profile = args.profile

        current_user = os.getlogin()
        if current_user in parser:
            self.profile = current_user

        self.profile = args.profile if args.profile else parser.default_section
