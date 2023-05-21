import { writeText } from "https://deno.land/x/copy_paste@v1.1.3/mod.ts";
import { stripColor } from "https://deno.land/std@0.187.0/fmt/colors.ts";

const apiKey = Deno.env.get("OPENAI_API_KEY");

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
    // deno-lint-ignore no-deprecated-deno-api
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
    // checks if $HOME/eggshell/.recordings/$pids exists

    const recordingPath = `${Deno.env.get(
      "EGGSHELL_PATH"
    )}/.recordings/${pid}.txt`;

    if (await exists(recordingPath)) {
      return recordingPath;
    }
  }

  return Promise.resolve(null);
}

function pidFromRecording(recording: string): string | null {
  const pid = recording.split("/").pop()?.split(".")[0];
  return pid ?? null;
}

async function recordingFromPath(recordingPath: string) {
  const text = await Deno.readTextFile(recordingPath);
  return stripColor(text);
}

// SESSION MANAGEMENT

async function getSession(recordingPath: string) {
  const pid = pidFromRecording(recordingPath);
  if (!pid) {
    return;
  }
  const sessionPath = `${Deno.env.get(
    "EGGSHELL_PATH"
  )}/.recordings/.session_${pid}`;

  const sessionExists = await exists(sessionPath);
  if (!sessionExists) {
    await Deno.create(sessionPath);
    await Deno.writeTextFile(sessionPath, JSON.stringify({ anchor: 0 }), {
      create: true,
    });
  }
  const sessionFile = await Deno.readTextFile(sessionPath);
  const session = JSON.parse(sessionFile);

  const recording = await recordingFromPath(recordingPath);

  const recordingLines = recording.split("\n");

  return {
    anchor: session.anchor,
    lines: recordingLines.slice(session.anchor),
  };
}

async function forgetSession(recordingPath: string) {
  const pid = pidFromRecording(recordingPath);
  if (!pid) {
    return;
  }
  const sessionPath = `${Deno.env.get(
    "EGGSHELL_PATH"
  )}/.recordings/.session_${pid}`;

  //set anchor to be the index of the last line of the session
  const sessionFile = await Deno.readTextFile(sessionPath);
  const session = JSON.parse(sessionFile);

  const recording = await Deno.readTextFile(recordingPath);

  const recordingLines = recording.split("\n");

  session.anchor = recordingLines.length;

  await Deno.writeTextFile(sessionPath, JSON.stringify(session), {});
}

async function handler() {
  const currentPid = Deno.pid;
  const ancestorPids = await getAllAncestorPids(currentPid);

  const recordingPath = await findRecording(ancestorPids);

  if (!recordingPath) {
    return;
  }

  const isReset = Deno.args[0] === "-c" && Deno.args.length === 1;

  if (isReset) {
    await forgetSession(recordingPath);
    return;
  }

  const session = await getSession(recordingPath);
  const prompt = Deno.args.join(" ");
  const generatedCommand = await fetchGeneratedCommand(
    prompt,
    session?.lines.join("\n") ?? ""
  );

  if (generatedCommand.length > 120 && !generatedCommand.startsWith("echo")) {
    console.log(generatedCommand);
  } else {
    writeText(generatedCommand);
  }
}

handler();
