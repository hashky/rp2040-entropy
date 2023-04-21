#!/bin/bash
test/pico_rng_test.py --performance --save   > figs/performance
tail figs/performance > figs/performance_stub
rm rdatz 2>/dev/null&&echo "removing old data..."||echo "old data absent"
test/pico_rng_test.py --size 2000000 > rdatz
test/pico_rng_analyze.py --save rdatz
