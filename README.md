# eggshell

eggshell brings OpenAI's GPT-4 to your CLI. GPT-4 will generate valid shell commands from your natural language input, thus saving lots of googling and browsing on stack overflow. And the best: You can use the AI capabilites directly from your shell, making the usage VERY easy.

## Examples

```
chegger:~$ q What time is it?
chegger:~$ date +%T
22:39:38
```

```
chegger:~$ q What is the weather like in Vienna?
chegger:~$ curl "wttr.in/Vienna?format=%C+%t"
Clear +22°C
```

## Usage
**The generated shell command is then copied to your clipboard. Simply paste it to the CLI and hit enter to execute it**. This gives you a way of checking what GPT-4 generated before actually executing the command, while still making it very easy to use.

As seen above you can simply call the eggshell script by using the `q` command on your CLI. Thus you can use your CLI the way you are used to and in addition you can use the `q` command to let GPT-4 generate a shell command for your query. Check out the examples to get a feeling for it.

Eggshell is set up to record all of your shell sessions (both input and output) and adds this session as context for your natural language queries. This way, GPT-4 generates tailored commands that solve your specific problem very reliably.


### Special commands

`q -c`: Clears the current session. This has two important implications:
1. GPT-4 "forgets" what has happened up to this point in the sesison. Thus, it cannot access any information from the past up to this point in time.
2. This means that fewer tokens are sent to GPT-4. Can decrease token usage a LOT when used frequently, thus drastically increasing speed and decreasing costs when querying GPT-4.

## Prerequisites

Eggshell is quite simple and was developed on `Ubuntu 20.04`. It works on that environment, and possibly on many linux distributions and possibly even mac. However, I have not really tested this.

The following software needs to be installed on your system:
 - [Deno](https://deno.com/)

## Setup

1. Install the eggshell deno script
```shell
git clone https://github.com/chegger/eggshell.git 
cd eggshell
deno install -A --name=q ./eggshell.ts
```

2. Add eggshell .recordings directory. The .recordings dir is ignored in the .gitignore file.
```shell
mkdir <absolute-path-to-git-repo>/.recordings
```

2. Setup bashrc. This will then automatically create a eggshell session when opening a CLI.
```shell
echo "source <absolute-path-to-git-repo>/shelly.sh" >> $HOME/.bashrc
echo "OPENAI_API_KEY=<your-openai-api-key> $HOME/.bashrc
```


## Implementation
Eggshell is implemented in a quite hacky way, however, I was happy to find a solution that meets important requirements:
 - I want to be able to use the `q` command in my normal environment. E.g. I DO NOT want there to be an interactive script that "replaces" the shell, potentially then limiting the user in a way.
 - I want to add context to the prompts sent to GPT-4. This requires the recoding of the full shell sessions (both user input and command ouptuts)
 - There must be a SIMPLE way to verify the generated  commands before actually executing them.






