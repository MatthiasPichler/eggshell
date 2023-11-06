from dataclasses import dataclass
from typing import Literal, TypedDict
from openai.types.chat import ChatCompletionToolParam


explain_tool: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "description": """
            This function explains something to the user. 
            It will be shown to them directly so you can address them directly. 
            Do not talk about them in the third person.
        """,
        "name": "explain",
        "parameters": {
            "type": "object",
            "required": ["explanation"],
            "properties": {
                "explanation": {"type": "string", "description": "The explanation."}
            },
        },
    },
}

suggest_command_tool: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "description": """
            This function shows a bash command to the user to be executed on the command line.
        """,
        "name": "suggest_command",
        "parameters": {
            "type": "object",
            "required": ["command"],
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to be executed.",
                }
            },
        },
    },
}


@dataclass
class ToolCall:
    id: str
    args: dict
    tokens: int
    name: str


class ExplainArguments(TypedDict):
    explanation: str


@dataclass
class ExplainCall(ToolCall):
    args: ExplainArguments
    name: Literal["explain"] = "explain"


class SuggestCommandArguments(TypedDict):
    command: str


@dataclass
class SuggestCommandCall(ToolCall):
    args: SuggestCommandArguments
    name: Literal["suggest_command"] = "suggest_command"
