#!/bin/bash

# cleanning services stored
rm -rf tmp
mkdir tmp

# downloading AWS commands
aws help | grep "^       +.o " | sed 's/       +.o //' | grep -v ' ' > tmp/aws.commands.txt
cat tmp/aws.commands.txt | while read c; do aws $c help | grep "^       +.o " | sed 's/       +.o //' | grep -v ' ' > tmp/aws.$c.txt; done 2> /dev/null
find tmp -size 0 | while read f; do rm -f $f; done
echo There are $(($(find tmp | wc -l) - 1 )) services
find tmp | grep 'tmp/' | grep -v 'tmp/aws.commands.txt' | while read f; do cnt=$(egrep -c -i -e "(start|pause|stop)" $f); if [ $cnt -eq 0 ]; then rm $f; fi; done
echo There are $(($(find tmp | wc -l) - 1 )) services with start and stop commands
find tmp | grep 'tmp/' | grep -v 'tmp/aws.commands.txt' | while read f; do cnt=$(egrep -c -i -e "(instance|cluster)" $f); if [ $cnt -eq 0 ]; then rm $f; fi; done
echo There are $(($(find tmp | wc -l) - 1 )) services can start and stop their instances
