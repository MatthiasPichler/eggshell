import openai
import os
import json

openai.api_key = os.environ.get("OPENAI_API_KEY")


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


def generate_next(prompt, recording):
    messages = [
        {
            "role": "system",
            "content": """
            You are the AI backend for an AI powered terminal. 
            You receive a recording of a shell and additionally a natural language request, and you must figure out an executable bash command that gets the request done or explain something about the output.
            Only ever respond with a function call to either the explain or suggest_command function.
            """,
        }
    ]

    if recording:
        messages.append({"role": "user", "content": recording})

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

    if "choices" not in response or len(response.choices) == 0:
        raise Exception("No generated command found")

    result = response.choices[0]

    if "finish_reason" not in result:
        raise Exception("No finish_reason found")

    if result.finish_reason == "length":
        raise Exception("Output too long")

    if result.finish_reason == "function_call":
        function_call = result.message.function_call
        args = json.load(function_call.arguments)
        name = function_call.name

        return {
            name: args,
        }

    raise Exception("Unknown finish_reason")
