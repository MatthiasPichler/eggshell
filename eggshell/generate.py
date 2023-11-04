from typing import Literal
import openai
import os
import json
from eggshell.functions import (
    ExplainFunctionCall,
    SuggestCommandFunctionCall,
    explain_function,
    suggest_command_function,
    ExplainArguments,
    SuggestCommandArguments,
)
from eggshell.log import logger, trace
from eggshell.sessions import Message, Session

openai.api_key = os.environ.get("OPENAI_API_KEY")


class OutputTruncated(Exception):
    def __init__(self):
        self.message = "Output too long"


class UnclearResponse(Exception):
    finish_reason: Literal["stop"] = "stop"
    tokens: int = 0

    def __init__(self, message: str, tokens: int = 0):
        self.message = message
        self.tokens = tokens


system_message = {
    "role": "system",
    "content": """
            You are the AI backend for an AI powered terminal called "eggshell". 
            You receive a recording of a shell and additionally a natural language request, and you must figure out an executable bash command that gets the request done or explain something about the output.
            Only ever respond with a function call to either the "explain" or "suggest_command" function.
            """,
}


@trace
def _gpt_message_from_session_message(message: Message):
    res = {
        "role": message.role,
        "content": message.content,
    }

    if message.finish_reason == "function_call":
        res["function_call"] = {
            "name": message.function_name,
            "arguments": message.function_arguments,
        }

    if message.role == "function":
        res["name"] = message.function_name

    return res


@trace
def generate_next(
    prompt: str, session: Session
) -> ExplainFunctionCall | SuggestCommandFunctionCall:
    messages = [system_message]

    session_messages = session.fetch_and_set_next_user_messages(prompt=prompt)

    messages.extend([_gpt_message_from_session_message(m) for m in session_messages])

    logger.debug("Generating response for messages %s", messages)

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

    if "choices" not in response or len(response.choices) == 0:  # type: ignore
        raise Exception("No generated command found")

    result = response.choices[0]  # type: ignore
    completion_tokens = response.usage.completion_tokens  # type: ignore

    logger.debug(result)

    if "finish_reason" not in result:
        raise Exception("No finish_reason found")

    if result.finish_reason == "length":
        raise OutputTruncated()

    if result.finish_reason == "stop":
        raise UnclearResponse(result.message.content, tokens=completion_tokens)

    if result.finish_reason == "function_call":
        function_call = result.message.function_call
        args = json.loads(function_call.arguments)
        name = function_call.name

        if name == "explain":
            return ExplainFunctionCall(
                args=ExplainArguments(**args), tokens=completion_tokens
            )

        if name == "suggest_command":
            return SuggestCommandFunctionCall(
                args=SuggestCommandArguments(**args), tokens=completion_tokens
            )

    raise Exception(f"Unknown finish_reason: {result.finish_reason}")
