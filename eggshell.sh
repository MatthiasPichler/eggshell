#!/bin/bash

trim() {
  local var="$*"
  var="${var#"${var%%[![:space:]]*}"}" # remove leading whitespace characters
  var="${var%"${var##*[![:space:]]}"}" # remove trailing whitespace characters
  echo -n "$var"
}

pid=$$
found=0

mkdir -p $EGGSHELL_PATH/.recordings

while [ $pid -ne 1 ]; do
  if [ -e "$EGGSHELL_PATH/.recordings/$pid.txt" ]; then
    found=1
    break
  fi
  pid=$(trim $(ps -o ppid= -p $pid))
done

if [$EGGSHELL_RECORDING]; then
  # don't record if we're already recording
  exit 0
fi

RECORDING_PATH=$EGGSHELL_PATH/.recordings/.recording_$$.txt

if [ $found -eq 0 ]; then
  if [[ "$(uname)" == "Darwin" ]]; then
    # macOS-specific actions
    EGGSHELL=1 EGGSHELL_RECORDING=$RECORDING_PATH PATH="$(pwd)/bin:${PATH}" script -Fq $EGGSHELL_PATH/.recordings/.recording_$$.txt
  elif [[ "$(uname)" == "Linux" ]]; then
    # Linux-specific actions
    EGGSHELL=1 EGGSHELL_RECORDING=$RECORDING_PATH PATH="$(pwd)/bin:${PATH}" script -fq $EGGSHELL_PATH/.recordings/.recording_$$.txt
  else
    # Handle other platforms
    echo "Unsupported platform."
    exit 1
  fi
fi
