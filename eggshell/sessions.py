from dataclasses import dataclass
import json
from eggshell.functions import FunctionCall
from eggshell.log import trace
import eggshell.recordings as recordings
import eggshell.config as config
import sqlite3
from typing import Literal


@dataclass
class Message:
    id: int
    finish_reason: Literal["stop", "length", "content_filter", "function_call"] | None
    role: Literal["system", "user", "assistant", "function"]
    content: str | None
    function_name: str | None
    function_arguments: str | None


class Session:
    connection: sqlite3.Connection

    @property
    def path(self):
        return config.eggshell_session

    def __init__(self):
        self.connection = sqlite3.connect(self.path)

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                finish_reason TEXT CHECK(finish_reason IN ('stop', 'length', 'content_filter', 'function_call')) NULL DEFAULT NULL,
                role TEXT CHECK(role IN ('system', 'user', 'assistant', 'function')) NOT NULL,
                content TEXT NULL DEFAULT NULL,
                function_name TEXT NULL DEFAULT NULL,
                function_arguments TEXT NULL DEFAULT NULL,
                tokens INTEGER CHECK(tokens >= 0) NULL,
                recording_byte_offset UNSIGNED BIG INT CHECK(tokens >= 0) NULL DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
            """,
        )
        self.connection.commit()

    def __str__(self):
        return f"Session(path={self.path})"

    def __repr__(self):
        return str(self)

    @trace
    def forget(self):
        recording = recordings.Recording(byte_offset=0)

        c = self.connection.cursor()
        c.execute("BEGIN TRANSACTION")

        c.execute("DELETE FROM messages;")
        c.execute(
            """
            INSERT INTO messages (role, content, recording_byte_offset) 
            VALUES ('user', 'The user cleared the history', ?);
            """,
            (recording.recording_size,),
        )
        self.connection.commit()

    @trace
    def fetch_and_set_next_user_messages(self, prompt: str) -> list[Message]:
        c = self.connection.cursor()
        res = c.execute("SELECT COALESCE(MAX(recording_byte_offset), 0) FROM messages;")
        (byte_offset,) = res.fetchone()

        recording = recordings.Recording(byte_offset=byte_offset)

        (recording_content, new_byte_offset) = recording.read_recording()

        c.execute(
            """
            INSERT INTO messages (role, content, recording_byte_offset) 
            VALUES 
                ('user', ?, ?),
                ('user', ?, NULL);
            """,
            (
                recording_content,
                new_byte_offset,
                prompt,
            ),
        )
        c.execute(
            """
            (
                SELECT id, finish_reason, role, content, function_name, function_arguments 
                FROM messages 
                ORDER BY id DESC
                LIMIT 100
            ) ORDER BY id ASC;
            """
        )
        messages = c.fetchall()
        self.connection.commit()

        return [Message(*m) for m in messages]

    @trace
    def record_other_response(self, response: str, tokens: int, finish_reason: str):
        c = self.connection.cursor()

        c.execute(
            """
            INSERT INTO messages (role, finish_reason, content, tokens) 
            VALUES ('assistant', ?, ?, ?);
            """,
            (
                finish_reason,
                response,
                tokens,
            ),
        )
        self.connection.commit()

    @trace
    def record_function_call(self, call: FunctionCall):
        c = self.connection.cursor()

        c.execute(
            """
            INSERT INTO messages (role, finish_reason, function_name, function_arguments, tokens) 
            VALUES ('assistant', 'function_call', ?, ?, ?);
            """,
            (
                call.name,
                json.dumps(call.args),
                call.tokens,
            ),
        )
        self.connection.commit()

    @trace
    def record_function_response(self, function_name: str, response: str):
        c = self.connection.cursor()

        c.execute(
            """
            INSERT INTO messages (role, function_name, content) 
            VALUES ('function', ?, ?);
            """,
            (function_name, response),
        )
        self.connection.commit()
