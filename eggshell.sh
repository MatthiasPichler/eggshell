#!/bin/bash

log() {
  if [ ! -z $DEBUG ]; then
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] DEBUG: $1"
  fi
}

if [ ! -z $EGGSHELL ]; then
  # don't record if we're already recording
  log "Already running in eggshell, exiting..."
  exit 0
fi

TMP_DIR=$(mktemp -d)
log "created temporary directory: $TMP_DIR"

# delete tmp dir on exit
trap "rm -rf $TMP_DIR" EXIT

RECORDING_PATH="${TMP_DIR}/recording.txt"
SESSION_PATH="${TMP_DIR}/session.json"

if [[ "$(uname)" == "Darwin" ]]; then
  # macOS-specific actions
  EGGSHELL=1 EGGSHELL_PATH=$TMP_DIR EGGSHELL_RECORDING=$RECORDING_PATH EGGSHELL_SESSION=$SESSION_PATH PATH="$(pwd)/bin:${PATH}" script -Fq $RECORDING_PATH
elif [[ "$(uname)" == "Linux" ]]; then
  # Linux-specific actions
  EGGSHELL=1 EGGSHELL_PATH=$TMP_DIR EGGSHELL_RECORDING=$RECORDING_PATH EGGSHELL_SESSION=$SESSION_PATH PATH="$(pwd)/bin:${PATH}" script -fq $RECORDING_PATH
else
  # Handle other platforms
  echo "Unsupported platform." >&2
  exit 1
fi
