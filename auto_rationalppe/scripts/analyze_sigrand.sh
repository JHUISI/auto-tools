#!/bin/sh

for file in gen/$1/*[0-9]_sigrand.ec; do printf "$file: "; grep "return " $file | sed 's,return ,,' | tr '\n' ' '; gtimeout 120 ./ggt.native interactive_1 $file | egrep "valid|Attack found"; done
