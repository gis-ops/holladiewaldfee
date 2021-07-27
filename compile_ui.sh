#!/bin/bash
for f in qrouting/ui/raw/*
do
  file_base=$(basename "$f")
  if [ "$file_base" != qrouting_dialog_base.ui ]
  then
    py_f=${file_base%%.*}
    echo "compiled $py_f"
    pyuic5  "$f" > qrouting/ui/"${py_f}_ui.py"
  fi
done