#!/usr/bin/env bash
if [ $# -ne 1 ]; then
    echo "[ USAGE ]: $0 <DIR_PATH>"
    exit
fi

ls -l
ls -l efs
echo "DIR_PATH is ${1}"

if [ -d "${1}" ]; then
  echo "1"
  exit
fi

echo "0"
