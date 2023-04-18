#!/bin/bash
test/pico_rng_test.py --performance & sleep 10&&echo ""&&sleep 2&& echo ""  && kill `pgrep -f pico_rng_test.py`
rm rdatz 2>/dev/null&&echo "removing old data..."||echo "old data absent"
test/pico_rng_test.py --size 2000000 > rdatz
test/pico_rng_analyze.py rdatz
