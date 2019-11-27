#!/bin/sh

for file in gen/$1/*[0-9].ec; do
  printf "$file: "
  grep '] in' $file | grep -v input | grep -v '\[\]'
  if grep "secure up to" $file >/dev/null; then
    printf "    "; grep "secure up to" $file
  fi
done
