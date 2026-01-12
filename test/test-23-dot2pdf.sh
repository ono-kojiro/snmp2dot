#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

. ./pythonpath.shrc

echo "1..1"

dotfile="output.dot"
pdffile="output.pdf"
cmd="dot -Tpdf -o ${pdffile} ${dotfile}"
echo $cmd
$cmd
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

