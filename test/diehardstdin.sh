#!/bin/bash
cat /dev/pico_rng|dieharder -a -g 200 -k 2 -Y 1 -m 2 

