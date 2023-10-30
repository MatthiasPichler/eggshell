import openai
import os
import json
from dataclasses import dataclass
from eggshell.log import logger, trace

openai.api_key = os.environ.get("OPENAI_API_KEY")


@dataclass
class ExplainArguments:
    explanation: str


@dataclass
class ExplainFunctionCall:
    args: ExplainArguments


@dataclass
class SuggestCommandArguments:
    command: str


@dataclass
class SuggestCommandFunctionCall:
    args: SuggestCommandArguments


class OutputTruncated(Exception):
    def __init__(self):
        self.message = "Output too long"


class UnclearResponse(Exception):
    def __init__(self, message):
        self.message = message


explain_function = {
    "description": "This function explains something to the user.",
    "name": "explain",
    "parameters": {
        "type": "object",
        "required": ["explanation"],
        "properties": {
            "explanation": {"type": "string", "description": "The explanation."}
        },
    },
}

suggest_command_function = {
    "description": "This function shows a command to the user to be executed on the command line.",
    "name": "suggest_command",
    "parameters": {
        "type": "object",
        "required": ["command"],
        "properties": {
            "command": {"type": "string", "description": "The command to be executed."}
        },
    },
}

system_message = {
    "role": "system",
    "content": """
            You are the AI backend for an AI powered terminal. 
            You receive a recording of a shell and additionally a natural language request, and you must figure out an executable bash command that gets the request done or explain something about the output.
            Only ever respond with a function call to either the explain or suggest_command function.
            """,
}


@trace
def generate_next(
    prompt: str, recording: str
) -> ExplainFunctionCall | SuggestCommandFunctionCall:
    messages = [system_message]

    if recording:
        messages.append({"role": "user", "content": str(recording)})

    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
        functions=[
            explain_function,
            suggest_command_function,
        ],
    )

    logger.debug(response)

    if "choices" not in response or len(response.choices) == 0:
        raise Exception("No generated command found")

    result = response.choices[0]

    logger.debug(result)

    if "finish_reason" not in result:
        raise Exception("No finish_reason found")

    if result.finish_reason == "length":
        raise OutputTruncated()

    if result.finish_reason == "stop":
        raise UnclearResponse(result.message.content)

    if result.finish_reason == "function_call":
        function_call = result.message.function_call
        args = json.loads(function_call.arguments)
        name = function_call.name

        if name == "explain":
            return ExplainFunctionCall(args=ExplainArguments(**args))

        if name == "suggest_command":
            return SuggestCommandFunctionCall(args=SuggestCommandArguments(**args))

    raise Exception(f"Unknown finish_reason: {result.finish_reason}")
