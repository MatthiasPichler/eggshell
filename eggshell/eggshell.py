import eggshell.generate as generate
import eggshell.sessions as sessions
from eggshell.log import logger, trace
import questionary
import subprocess
from argparse import Namespace


class Eggshell:
    session: sessions.Session
    args: Namespace

    def __init__(self, args):
        self.args = args

        if args.verbose == 1:
            logger.setLevel("INFO")
        elif args.verbose == 2:
            logger.setLevel("DEBUG")
        elif args.verbose >= 3:
            logger.setLevel("TRACE")

        self.session = sessions.Session()

    @trace
    def run(self):
        if self.args.clear:
            self.session.forget()
        else:
            self.generate()

    @trace
    def generate(self):
        generated_command = None

        try:
            generated_command = generate.generate_next(
                prompt=self.args.prompt, session=self.session
            )
        except generate.OutputTruncated as e:
            print("The generated output was too long:")
            print(f"{e.message}...[truncated].")
            print("If the output is insufficient please try again.")
            return
        except generate.UnclearResponse as e:
            print("The AI was not able to generate a command:")
            print(e.message)
            print("Please try again.")
            self.session.record_other_response(
                response=e.message, tokens=e.tokens, finish_reason=e.finish_reason
            )
        except Exception as e:
            logger.error(e)
            exit(1)

        logger.debug(f"Generated command: {generated_command}")

        if isinstance(generated_command, generate.ExplainFunctionCall):
            self.session.record_function_call(generated_command)
            print(generated_command.args["explanation"])
            self.session.record_function_response(
                function_name=generated_command.name,
                response=generated_command.args["explanation"],
            )
        elif isinstance(generated_command, generate.SuggestCommandFunctionCall):
            self.session.record_function_call(generated_command)
            command = generated_command.args["command"]

            should_execute = questionary.confirm(f"execute: {command}").ask()

            if should_execute:
                self.session.record_function_response(
                    function_name=generated_command.name,
                    response=f'Command: "{command}" was executed.',
                )
                subprocess.run(f"exec {command}", shell=True)
            else:
                self.session.record_function_response(
                    function_name=generated_command.name,
                    response=f'Command: "{command}" was not executed.',
                )
