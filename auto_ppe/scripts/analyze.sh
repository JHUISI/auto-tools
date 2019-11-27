#!/bin/sh

for file in gen/$1/*[0-9].ec; do
  printf "$file: "; grep "return " $file | sed 's,return ,,' | \
   tr '\n' ' '; gtimeout 120 ./ggt.native interactive_2 $file > $file.result_2
    egrep "valid|Attack found" $file.result_2
done
