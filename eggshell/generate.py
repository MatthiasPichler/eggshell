from typing import Literal
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionToolMessageParam,
)
import os
import json
from eggshell.tools import (
    ExplainCall,
    SuggestCommandCall,
    explain_tool,
    suggest_command_tool,
    ExplainArguments,
    SuggestCommandArguments,
)
from eggshell.log import logger, trace
from eggshell.sessions import Message, Session

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class OutputTruncated(Exception):
    def __init__(self):
        self.message = "Output too long"


class UnclearResponse(Exception):
    finish_reason: Literal["stop"] = "stop"
    tokens: int = 0

    def __init__(self, message: str, tokens: int = 0):
        self.message = message
        self.tokens = tokens


system_message: ChatCompletionSystemMessageParam = {
    "role": "system",
    "content": """
            You are the AI backend for an AI powered terminal called "eggshell".
            Messages will contain a recoding of the shell session followed in the next message by the natural language request of the user.
            The recording is split between messages whenever the AI is called.
            You must figure out an executable bash command that gets the request done or explain something about the output.
            Only ever respond with a tool call to either the "explain" or "suggest_command" function.
            """.replace("\t", "")
    .replace("\n", " ")
    .strip(),
}


@trace
def _gpt_message_from_session_message(message: Message) -> ChatCompletionMessageParam:
    if message.role == "assistant":
        res = ChatCompletionAssistantMessageParam(
            {
                "role": "assistant",
                "content": str(message.content),
            }
        )

        if message.finish_reason == "tool_calls":
            res["tool_calls"] = [
                {
                    "id": str(message.tool_call_id),
                    "type": "function",
                    "function": {
                        "name": str(message.tool_function_name),
                        "arguments": str(message.tool_function_arguments),
                    },
                }
            ]

        return res
    elif message.role == "user":
        return ChatCompletionUserMessageParam(
            {
                "role": "user",
                "content": message.content,
            }
        )
    else:
        return ChatCompletionToolMessageParam(
            {
                "role": "tool",
                "content": message.content,
                "tool_call_id": str(message.tool_call_id),
            }
        )


@trace
def generate_next(prompt: str, session: Session) -> ExplainCall | SuggestCommandCall:
    messages: list[ChatCompletionMessageParam] = [system_message]

    session_messages = session.fetch_and_set_next_user_messages(prompt=prompt)

    messages.extend([_gpt_message_from_session_message(m) for m in session_messages])

    logger.debug("Generating response for messages %s", messages)

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
        tools=[
            explain_tool,
            suggest_command_tool,
        ],
    )

    logger.debug(response)

    result = response.choices[0]  # type: ignore
    completion_tokens = response.usage.completion_tokens  # type: ignore

    logger.debug(result)

    if result.finish_reason == "length":
        raise OutputTruncated()

    if result.finish_reason == "stop":
        raise UnclearResponse(str(result.message.content), tokens=completion_tokens)

    if result.finish_reason == "tool_calls" and result.message.tool_calls:
        call = result.message.tool_calls[0]
        id = call.id
        args = json.loads(call.function.arguments)
        name = call.function.name

        if name == "explain":
            return ExplainCall(
                id=id, args=ExplainArguments(**args), tokens=completion_tokens
            )

        if name == "suggest_command":
            return SuggestCommandCall(
                id=id, args=SuggestCommandArguments(**args), tokens=completion_tokens
            )

    raise Exception(f"Unknown finish_reason: {result.finish_reason}")
