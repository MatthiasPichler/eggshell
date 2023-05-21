import { writeText } from "https://deno.land/x/copy_paste@v1.1.3/mod.ts";

type Message = { role: "user" | "assistant" | "system"; content: string };

const apiKey = Deno.env.get("OPENAI_API_KEY");
console.log(apiKey);

async function fetchGeneratedCommand(
  prompt: string,
  recording: string | null
): Promise<string> {

  const messages = [
    {
      role: "system",
      content:
        "You are the AI backend for an AI powered terminal. You receive a recording of a shell and additionall a natural language request and you must figure out an executable bash command that gets the request done. It is extremely important that the response is always and executable command for the ubuntu terminal.",
    },
  ];

  if (recording) {
    messages.push({ role: "user", content: recording });
  }

  messages.push({ role: "user", content: prompt });

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      messages,
      max_tokens: 1000,
      n: 1,
      stop: null,
      temperature: 0.5,
      model: "gpt-4",
    }),
  });

  const data = await response.json();
  if (data.choices && data.choices.length > 0) {
    return data.choices[0].message.content;
  } else {
    console.log(data);
    throw new Error("No generated command found");
  }
}

// RECORDING MANAGEMENT
async function getParentPid(pid: number): Promise<number | null> {
  try {
    const process = Deno.run({
      cmd: ["ps", "-o", "ppid=", "-p", `${pid}`],
      stdout: "piped",
      stderr: "piped",
    });

    const output = await process.output();
    const error = await process.stderrOutput();

    if (error.length > 0) {
      throw new TextDecoder().decode(error);
    }

    const parentPid = parseInt(new TextDecoder().decode(output).trim());
    return isNaN(parentPid) ? null : parentPid;
  } catch (error) {
    console.error(`Error getting parent PID: ${error}`);
    return null;
  }
}

async function getAllAncestorPids(pid: number): Promise<number[]> {
  const ancestorPids: number[] = [];
  let parentPid = await getParentPid(pid);

  while (parentPid) {
    ancestorPids.push(parentPid);
    parentPid = await getParentPid(parentPid);
  }

  return ancestorPids;
}

const exists = async (filename: string): Promise<boolean> => {
  try {
    await Deno.stat(filename);
    // successful, file or directory must exist
    return true;
  } catch (error) {
    if (error instanceof Deno.errors.NotFound) {
      // file or directory does not exist
      return false;
    } else {
      // unexpected error, maybe permissions, pass it along
      throw error;
    }
  }
};

async function findRecording(pids: number[]): Promise<string | null> {
  for (const pid of pids) {
    // checks if $HOME/aiterminal/.recordings/$pids exists

    const recordingPath = `${Deno.env.get(
      "HOME"
    )}/aiterminal/.recordings/${pid}.txt`;

    if (await exists(recordingPath)) {
      return recordingPath;
    }
  }

  return Promise.resolve(null);
}

// SESSION FROM RECORDING
function removeAnsiEscapeCodes(str: string): string {
  return (
    str
      // deno-lint-ignore no-control-regex
      .replace(/\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])/g, "")
      // deno-lint-ignore no-control-regex
      .replace(/\x1b\[[0-9;]*[a-zA-Z]/g, "")
  );
}

async function recordingFromPath(recordingPath: string) {
  const text = await Deno.readTextFile(recordingPath);
  return removeAnsiEscapeCodes(text);
}

//OUTPUT HELPER

//HANDLER

async function handler() {
  const currentPid = Deno.pid;
  const ancestorPids = await getAllAncestorPids(currentPid);

  const recordingPath = await findRecording(ancestorPids);

  let recording = null;

  if (recordingPath) {
    recording = await recordingFromPath(recordingPath);
  }

  const prompt = Deno.args.join(" ");
  const generatedCommand = await fetchGeneratedCommand(prompt, recording);

  if (generatedCommand.length > 120 && !generatedCommand.startsWith("echo")) {
    console.log(generatedCommand);
  } else {
    writeText(generatedCommand);
  }
}

handler();
