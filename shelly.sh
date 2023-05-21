#!/bin/bash

trim() {
  local var="$*"
  var="${var#"${var%%[![:space:]]*}"}"   # remove leading whitespace characters
  var="${var%"${var##*[![:space:]]}"}"   # remove trailing whitespace characters
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

if [ $found -eq 0 ]; then
  script -fq $EGGSHELL_PATH/.recordings/$$.txt
fi
