#!/bin/bash
test/pico_rng_test.py --size 1073741824 > sample.rng
echo \`\`\` > figs/diehard.txt
dieharder -a -g 201 -k 2 -Y 1 -m 2 -f sample.rng >> figs/diehard.txt
echo \`\`\` >> figs/diehard.txt
#cat /dev/pico_rng|dieharder -a -g 200 -k 2 -Y 1 -m 2 

