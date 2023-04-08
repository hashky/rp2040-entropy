#!/bin/bash
test/pico_rng_test.py --performance&sleep 2&&echo "       "&&sleep 2&&echo "       "&&sleep 2&&echo "         "&&kill `pgrep -f pico_rng_test.py`
test/pico_rng_test.py --size 1000000 > rdatz
test/pico_rng_analyze.py rdatz
