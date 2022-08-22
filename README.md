# Raspberry Pi Pico Random Number Generator

** This fork includes an enhanced RNG to produce a true RNG. **

A basic random number generator that generates numbers from enviromental noise with the onboard DAC of the Raspberry Pi Pico. The project uses the Raspberry Pi Pico USB dev_lowlevel as a starting point. The Pico RNG is not meant to be FIPS 140-2 compliant as a stand-alone device by any means. However it does supply the Linux Kernel with random bits that is used with the appropriate entropy to achieve FIPS 140-2 compliant random numbers. Maybe one day the next gen Pico's will include an onboard crypto module.

## Project Goals
* Raspberry Pi Pico firmware generates random numbers as a USB Endpoint.
* Linux Kernel Module (aka driver) provides random numbers to the Kernel.
* Driver can transmit random numbers on demand to the system and/or user processes via a character device.


## Prerequisites

* Raspberry Pi Pico development environment. See [Raspberry Pi Pico Getting Started Documentation](https://www.raspberrypi.org/documentation/pico/getting-started/)
* Linux Kernel development headers


## Building
The entire project uses CMake to keep with Rasberry Pi Pico's development environment and project setup instructions.

```bash
# Create build directory
mkdir build

# Change to the build directory
cd build

# Run cmake
cmake ..

# Run make
make
```

## Install

The driver can be installed from the build directory using the traditional insmod command.

```bash
# Assumes CWD is 'build/'
# debug will enable debug log level
# timeout will set the usb endpoint timeout. Currently defaults to 100 msecs
sudo insmod driver/pico_rng.ko [debug=1] [timeout=<msec timeout>]
```

The Pico firmware is installed thorugh the normal process as outlined in the Raspberry Pi Pico Development Documentation.

* Unplug the Pico from the host.
* Plug the Pico into the host while holding the 'boot' button.
* Mount the Pico ```sudo mount /dev/sdb1 /mnt```. Note /dev/sdb1 could be different you. Use ```sudo dmesg``` to find out what device the Pico shows up as on your system.
* Copy the uf2 file to the Pico ```sudo cp firmware/pico_rng.uf2 /mnt```.
* Umount the pico ```sudo umount /mnt```.

## Testing

You can test Pico RNG firmware with the [pico_rng_test.py](firmware/pico_rng_test.py) script.

```bash
# Running with --performance will measure the devices' KB/s.
# if the kernel module has been installed, then the test tool will use /dev/pico_rng otherwise python's libusb implementation will be used.
sudo firmware/pico_rng_test.py [--performance] [--size] [--endless]
```

You can also test the Kernel's random number pool that contains random numbers from the Pico
![Pico Random Numbers](pico-rng.gif)

## Analysis

A set of random samples can be analyzed with the [pico_rng_analyze.py](firmware/pico_rng_analyze.py) script.

For generating a set of samples, the following code can be executed:
```bash
$ python3 firmware/pico_rng_test.py --size 1073741824 > sample.rng
```
will produce a 1 GB file containing random bytes.

Then
```bash
$ python3 firmware/pico_rng_analyze.py sample.rng
```
will produce two figures:

![fig1](https://user-images.githubusercontent.com/55573252/185908242-9fac9e7c-bfd2-440b-bd1d-045b571ed010.png)

Fig. 1 depicts the distribution of the bytes, from `0` to `255`. Ideally, it must be a uniform distribution, with mean equal to `127.5`.

![fig2](https://user-images.githubusercontent.com/55573252/185908272-42973878-7c4f-45ec-8492-6878f8a0bfa6.png)

Fig. 2 depicts the distribution of chi square tests and excess percentages. Ideally, the distribution of chi square tests must follow a chi square distribution with mean at `255`. Excess percentage distribution must follow a uniform distribution.

Pico-rng is also tested with `ent`, `rngtest` and `dieharder` tests. These are the results obtained with pico-rng:

```
$ ent sample.rng
Entropy = 7.999999 bits per byte.

Optimum compression would reduce the size
of this 1073741824 byte file by 0 percent.

Chi square distribution for 1073741824 samples is 839.56, and randomly
would exceed this value less than 0.01 percent of the times.

Arithmetic mean value of data bytes is 127.4993 (127.5 = random).
Monte Carlo value for Pi is 3.141625006 (error 0.00 percent).
Serial correlation coefficient is 0.000006 (totally uncorrelated = 0.0).
```
- Entropy test should produce an ideal result of `8`, as each byte has `8` bits.
- Optimum compression test should produce an ideal result of 0 percent.
- Chi square should be called with different sample tests and produce a chi square distribution.
- Arithmetic mean should produce an ideal result of `127.5`.
- Pi test should be equal to pi number.
- Serial correlation should be `0`.

These results show that pico-rng is pretty random.


```bash
$ cat sample.rng | rngtest
rngtest 2-unofficial-mt.14
Copyright (c) 2004 by Henrique de Moraes Holschuh
This is free software; see the source for copying conditions.  There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

rngtest: starting FIPS tests...
rngtest: entropy source exhausted!
rngtest: bits received from input: 8589934592
rngtest: FIPS 140-2 successes: 429141
rngtest: FIPS 140-2 failures: 355
rngtest: FIPS 140-2(2001-10-10) Monobit: 42
rngtest: FIPS 140-2(2001-10-10) Poker: 41
rngtest: FIPS 140-2(2001-10-10) Runs: 138
rngtest: FIPS 140-2(2001-10-10) Long run: 136
rngtest: FIPS 140-2(2001-10-10) Continuous run: 0
rngtest: input channel speed: (min=9661835.749; avg=23078154805.083; max=0.000)bits/s
rngtest: FIPS tests speed: (min=5.699; avg=239.429; max=261.281)Mibits/s
rngtest: Program run time: 34612429 microseconds
```

In these results, we have a total number of trials `429496 (429141+355)`.
- The acceptable result of Monobit test is `1` failed trial for every `9662` trials. For `429496` trials, the number of failed trials should be less than `429496/9662=44.45`.
- The acceptable result of Poker test is `1` failed trial for every `10078` trials. For `429496` trials, the number of failed trials should be less than `42.62`.

```bash
$ dieharder -a -g 201 -k 2 -Y 1 -m 2 -f sample.rng
#=============================================================================#
#            dieharder version 3.31.1 Copyright 2003 Robert G. Brown          #
#=============================================================================#
   rng_name    |           filename             |rands/second|
 file_input_raw|                      batch1.rng|  3.57e+07  |
#=============================================================================#
        test_name   |ntup| tsamples |psamples|  p-value |Assessment
#=============================================================================#
   diehard_birthdays|   0|       100|     200|0.17739498|  PASSED
      diehard_operm5|   0|   1000000|     200|0.97387049|  PASSED
# The file file_input_raw was rewound 1 times
  diehard_rank_32x32|   0|     40000|     200|0.37394022|  PASSED
# The file file_input_raw was rewound 2 times
    diehard_rank_6x8|   0|    100000|     200|0.09038266|  PASSED
# The file file_input_raw was rewound 2 times
   diehard_bitstream|   0|   2097152|     200|0.71785604|  PASSED
# The file file_input_raw was rewound 4 times
        diehard_opso|   0|   2097152|     200|0.37146068|  PASSED
# The file file_input_raw was rewound 5 times
        diehard_oqso|   0|   2097152|     200|0.35763562|  PASSED
# The file file_input_raw was rewound 5 times
         diehard_dna|   0|   2097152|     200|0.01889729|  PASSED
# The file file_input_raw was rewound 5 times
diehard_count_1s_str|   0|    256000|     200|0.63258197|  PASSED
# The file file_input_raw was rewound 6 times
diehard_count_1s_byt|   0|    256000|     200|0.65359815|  PASSED
# The file file_input_raw was rewound 6 times
 diehard_parking_lot|   0|     12000|     200|0.83176205|  PASSED
# The file file_input_raw was rewound 6 times
    diehard_2dsphere|   2|      8000|     200|0.64543002|  PASSED
# The file file_input_raw was rewound 6 times
    diehard_3dsphere|   3|      4000|     200|0.01258942|  PASSED
# The file file_input_raw was rewound 8 times
     diehard_squeeze|   0|    100000|     200|0.67578527|  PASSED
# The file file_input_raw was rewound 8 times
        diehard_sums|   0|       100|     200|0.23981668|  PASSED
# The file file_input_raw was rewound 8 times
        diehard_runs|   0|    100000|     200|0.77427455|  PASSED
        diehard_runs|   0|    100000|     200|0.08390099|  PASSED
# The file file_input_raw was rewound 9 times
       diehard_craps|   0|    200000|     200|0.59348655|  PASSED
       diehard_craps|   0|    200000|     200|0.23828837|  PASSED
# The file file_input_raw was rewound 24 times
 marsaglia_tsang_gcd|   0|  10000000|     200|0.15517856|  PASSED
 marsaglia_tsang_gcd|   0|  10000000|     200|0.00447239|   WEAK
# The file file_input_raw was rewound 31 times
 marsaglia_tsang_gcd|   0|  10000000|     300|0.02554040|  PASSED
 marsaglia_tsang_gcd|   0|  10000000|     300|0.00100578|   WEAK
# The file file_input_raw was rewound 39 times
 marsaglia_tsang_gcd|   0|  10000000|     400|0.00299305|   WEAK
 marsaglia_tsang_gcd|   0|  10000000|     400|0.00008767|   WEAK
# The file file_input_raw was rewound 46 times
 marsaglia_tsang_gcd|   0|  10000000|     500|0.00201489|   WEAK
 marsaglia_tsang_gcd|   0|  10000000|     500|0.00004067|   WEAK
# The file file_input_raw was rewound 54 times
 marsaglia_tsang_gcd|   0|  10000000|     600|0.00028460|   WEAK
 marsaglia_tsang_gcd|   0|  10000000|     600|0.00000323|   WEAK
# The file file_input_raw was rewound 61 times
 marsaglia_tsang_gcd|   0|  10000000|     700|0.00004334|   WEAK
 marsaglia_tsang_gcd|   0|  10000000|     700|0.00000055|  FAILED
# The file file_input_raw was rewound 61 times
         sts_monobit|   1|    100000|     200|0.11868265|  PASSED
# The file file_input_raw was rewound 61 times
            sts_runs|   2|    100000|     200|0.55674493|  PASSED
# The file file_input_raw was rewound 61 times
          sts_serial|   1|    100000|     200|0.99669244|   WEAK
          sts_serial|   2|    100000|     200|0.46102720|  PASSED
          sts_serial|   3|    100000|     200|0.44562932|  PASSED
          sts_serial|   3|    100000|     200|0.84230024|  PASSED
          sts_serial|   4|    100000|     200|0.98548763|  PASSED
          sts_serial|   4|    100000|     200|0.57495245|  PASSED
          sts_serial|   5|    100000|     200|0.77085975|  PASSED
          sts_serial|   5|    100000|     200|0.56476358|  PASSED
          sts_serial|   6|    100000|     200|0.45650075|  PASSED
          sts_serial|   6|    100000|     200|0.05289356|  PASSED
          sts_serial|   7|    100000|     200|0.27201114|  PASSED
          sts_serial|   7|    100000|     200|0.76400695|  PASSED
          sts_serial|   8|    100000|     200|0.62348338|  PASSED
          sts_serial|   8|    100000|     200|0.57277685|  PASSED
          sts_serial|   9|    100000|     200|0.38071419|  PASSED
          sts_serial|   9|    100000|     200|0.07625829|  PASSED
          sts_serial|  10|    100000|     200|0.47989859|  PASSED
          sts_serial|  10|    100000|     200|0.11112817|  PASSED
          sts_serial|  11|    100000|     200|0.92833035|  PASSED
          sts_serial|  11|    100000|     200|0.69376394|  PASSED
          sts_serial|  12|    100000|     200|0.84887524|  PASSED
          sts_serial|  12|    100000|     200|0.97617601|  PASSED
          sts_serial|  13|    100000|     200|0.65397230|  PASSED
          sts_serial|  13|    100000|     200|0.56436970|  PASSED
          sts_serial|  14|    100000|     200|0.51868029|  PASSED
          sts_serial|  14|    100000|     200|0.92953669|  PASSED
          sts_serial|  15|    100000|     200|0.85158213|  PASSED
          sts_serial|  15|    100000|     200|0.93993540|  PASSED
          sts_serial|  16|    100000|     200|0.35998600|  PASSED
          sts_serial|  16|    100000|     200|0.20807684|  PASSED
# The file file_input_raw was rewound 61 times
          sts_serial|   1|    100000|     300|0.19573096|  PASSED
          sts_serial|   2|    100000|     300|0.85406665|  PASSED
          sts_serial|   3|    100000|     300|0.06590447|  PASSED
          sts_serial|   3|    100000|     300|0.45707402|  PASSED
          sts_serial|   4|    100000|     300|0.44442263|  PASSED
          sts_serial|   4|    100000|     300|0.52775404|  PASSED
          sts_serial|   5|    100000|     300|0.40217529|  PASSED
          sts_serial|   5|    100000|     300|0.06010705|  PASSED
          sts_serial|   6|    100000|     300|0.08040223|  PASSED
          sts_serial|   6|    100000|     300|0.00547743|  PASSED
          sts_serial|   7|    100000|     300|0.24575210|  PASSED
          sts_serial|   7|    100000|     300|0.28977315|  PASSED
          sts_serial|   8|    100000|     300|0.36868885|  PASSED
          sts_serial|   8|    100000|     300|0.49522777|  PASSED
          sts_serial|   9|    100000|     300|0.40957917|  PASSED
          sts_serial|   9|    100000|     300|0.09110499|  PASSED
          sts_serial|  10|    100000|     300|0.77559781|  PASSED
          sts_serial|  10|    100000|     300|0.19716611|  PASSED
          sts_serial|  11|    100000|     300|0.80459107|  PASSED
          sts_serial|  11|    100000|     300|0.44572782|  PASSED
          sts_serial|  12|    100000|     300|0.20184427|  PASSED
          sts_serial|  12|    100000|     300|0.60780140|  PASSED
          sts_serial|  13|    100000|     300|0.76273905|  PASSED
          sts_serial|  13|    100000|     300|0.60473178|  PASSED
          sts_serial|  14|    100000|     300|0.24687487|  PASSED
          sts_serial|  14|    100000|     300|0.66722555|  PASSED
          sts_serial|  15|    100000|     300|0.85162176|  PASSED
          sts_serial|  15|    100000|     300|0.81632309|  PASSED
          sts_serial|  16|    100000|     300|0.72398028|  PASSED
          sts_serial|  16|    100000|     300|0.26061444|  PASSED
# The file file_input_raw was rewound 61 times
         rgb_bitdist|   1|    100000|     200|0.80303319|  PASSED
# The file file_input_raw was rewound 62 times
         rgb_bitdist|   2|    100000|     200|0.44511426|  PASSED
# The file file_input_raw was rewound 62 times
         rgb_bitdist|   3|    100000|     200|0.15306427|  PASSED
# The file file_input_raw was rewound 63 times
         rgb_bitdist|   4|    100000|     200|0.52424083|  PASSED
# The file file_input_raw was rewound 64 times
         rgb_bitdist|   5|    100000|     200|0.62602197|  PASSED
# The file file_input_raw was rewound 64 times
         rgb_bitdist|   6|    100000|     200|0.27582205|  PASSED
# The file file_input_raw was rewound 65 times
         rgb_bitdist|   7|    100000|     200|0.83928387|  PASSED
# The file file_input_raw was rewound 67 times
         rgb_bitdist|   8|    100000|     200|0.78920891|  PASSED
# The file file_input_raw was rewound 68 times
         rgb_bitdist|   9|    100000|     200|0.10426661|  PASSED
# The file file_input_raw was rewound 69 times
         rgb_bitdist|  10|    100000|     200|0.56345552|  PASSED
# The file file_input_raw was rewound 71 times
         rgb_bitdist|  11|    100000|     200|0.67837353|  PASSED
# The file file_input_raw was rewound 73 times
         rgb_bitdist|  12|    100000|     200|0.77285406|  PASSED
# The file file_input_raw was rewound 73 times
rgb_minimum_distance|   2|     10000|    2000|0.99326519|  PASSED
# The file file_input_raw was rewound 73 times
rgb_minimum_distance|   3|     10000|    2000|0.89490386|  PASSED
# The file file_input_raw was rewound 74 times
rgb_minimum_distance|   4|     10000|    2000|0.63482997|  PASSED
# The file file_input_raw was rewound 74 times
rgb_minimum_distance|   5|     10000|    2000|0.04956198|  PASSED
# The file file_input_raw was rewound 74 times
    rgb_permutations|   2|    100000|     200|0.59389551|  PASSED
# The file file_input_raw was rewound 74 times
    rgb_permutations|   3|    100000|     200|0.84473217|  PASSED
# The file file_input_raw was rewound 75 times
    rgb_permutations|   4|    100000|     200|0.67098621|  PASSED
# The file file_input_raw was rewound 75 times
    rgb_permutations|   5|    100000|     200|0.71477222|  PASSED
# The file file_input_raw was rewound 76 times
      rgb_lagged_sum|   0|   1000000|     200|0.20844392|  PASSED
# The file file_input_raw was rewound 77 times
      rgb_lagged_sum|   1|   1000000|     200|0.52704060|  PASSED
# The file file_input_raw was rewound 79 times
      rgb_lagged_sum|   2|   1000000|     200|0.68631913|  PASSED
# The file file_input_raw was rewound 82 times
      rgb_lagged_sum|   3|   1000000|     200|0.04971017|  PASSED
# The file file_input_raw was rewound 86 times
      rgb_lagged_sum|   4|   1000000|     200|0.11342937|  PASSED
# The file file_input_raw was rewound 91 times
      rgb_lagged_sum|   5|   1000000|     200|0.08126696|  PASSED
# The file file_input_raw was rewound 96 times
      rgb_lagged_sum|   6|   1000000|     200|0.20866831|  PASSED
# The file file_input_raw was rewound 102 times
      rgb_lagged_sum|   7|   1000000|     200|0.52239049|  PASSED
# The file file_input_raw was rewound 109 times
      rgb_lagged_sum|   8|   1000000|     200|0.68232225|  PASSED
# The file file_input_raw was rewound 116 times
      rgb_lagged_sum|   9|   1000000|     200|0.13755031|  PASSED
# The file file_input_raw was rewound 124 times
      rgb_lagged_sum|  10|   1000000|     200|0.82473876|  PASSED
# The file file_input_raw was rewound 133 times
      rgb_lagged_sum|  11|   1000000|     200|0.10861154|  PASSED
# The file file_input_raw was rewound 143 times
      rgb_lagged_sum|  12|   1000000|     200|0.10432254|  PASSED
# The file file_input_raw was rewound 153 times
      rgb_lagged_sum|  13|   1000000|     200|0.18082599|  PASSED
# The file file_input_raw was rewound 164 times
      rgb_lagged_sum|  14|   1000000|     200|0.13220862|  PASSED
# The file file_input_raw was rewound 176 times
      rgb_lagged_sum|  15|   1000000|     200|0.08158678|  PASSED
# The file file_input_raw was rewound 189 times
      rgb_lagged_sum|  16|   1000000|     200|0.02760994|  PASSED
# The file file_input_raw was rewound 202 times
      rgb_lagged_sum|  17|   1000000|     200|0.14079614|  PASSED
# The file file_input_raw was rewound 217 times
      rgb_lagged_sum|  18|   1000000|     200|0.23268911|  PASSED
# The file file_input_raw was rewound 231 times
      rgb_lagged_sum|  19|   1000000|     200|0.50758360|  PASSED
# The file file_input_raw was rewound 247 times
      rgb_lagged_sum|  20|   1000000|     200|0.66798605|  PASSED
# The file file_input_raw was rewound 263 times
      rgb_lagged_sum|  21|   1000000|     200|0.13844382|  PASSED
# The file file_input_raw was rewound 281 times
      rgb_lagged_sum|  22|   1000000|     200|0.44084188|  PASSED
# The file file_input_raw was rewound 299 times
      rgb_lagged_sum|  23|   1000000|     200|0.90104158|  PASSED
# The file file_input_raw was rewound 317 times
      rgb_lagged_sum|  24|   1000000|     200|0.80347842|  PASSED
# The file file_input_raw was rewound 337 times
      rgb_lagged_sum|  25|   1000000|     200|0.07703809|  PASSED
# The file file_input_raw was rewound 357 times
      rgb_lagged_sum|  26|   1000000|     200|0.69854447|  PASSED
# The file file_input_raw was rewound 377 times
      rgb_lagged_sum|  27|   1000000|     200|0.26315861|  PASSED
# The file file_input_raw was rewound 399 times
      rgb_lagged_sum|  28|   1000000|     200|0.58852190|  PASSED
# The file file_input_raw was rewound 421 times
      rgb_lagged_sum|  29|   1000000|     200|0.42224280|  PASSED
# The file file_input_raw was rewound 445 times
      rgb_lagged_sum|  30|   1000000|     200|0.18274721|  PASSED
# The file file_input_raw was rewound 468 times
      rgb_lagged_sum|  31|   1000000|     200|0.18647377|  PASSED
# The file file_input_raw was rewound 493 times
      rgb_lagged_sum|  32|   1000000|     200|0.83130153|  PASSED
# The file file_input_raw was rewound 493 times
     rgb_kstest_test|   0|     10000|    2000|0.05507241|  PASSED
# The file file_input_raw was rewound 494 times
     dab_bytedistrib|   0|  51200000|       2|0.22222222|  PASSED
# The file file_input_raw was rewound 494 times
             dab_dct| 256|     50000|       2|0.98359769|  PASSED
Preparing to run test 207.  ntuple = 0
# The file file_input_raw was rewound 495 times
        dab_filltree|  32|  15000000|       2|0.75609132|  PASSED
        dab_filltree|  32|  15000000|       2|1.00000000|  FAILED
Preparing to run test 208.  ntuple = 0
# The file file_input_raw was rewound 495 times
       dab_filltree2|   0|   5000000|       2|1.00000000|  FAILED
       dab_filltree2|   1|   5000000|       2|1.00000000|  FAILED
Preparing to run test 209.  ntuple = 0
# The file file_input_raw was rewound 496 times
        dab_monobit2|  12|  65000000|       2|1.00000000|  FAILED
```

## Remove
```bash
sudo rmmod pico_rng
```

# About the random number generator
Raspberry Pi Pico has a Ring Oscillator (ROSC) that produces a random bit, despite that it is not intended for secure applications. In general, ROSC produce weak/correlated random bits. Thus, we increase the randomness by adding more entropy sources:
- A random word produced by ROSC.
- A current timestamp.
- A read from an open GPIO pin.

The produced random word is then passed through a whitener. In particular, the Fowler–Noll–Vo hash function is used as a whitener.

Finally, the word is packed into a byte array and returned to the host.

The performance of this RNG can be analyzed with [pico_rng_analyze.py](firmware/pico_rng_analyze.py) script and typical tools, such as `ent`, `rngtest` or `dierharder`. See results above.

### License

This project is licensed under the BSD 3-Clause "New" or "Revised" License - see the [LICENSE.md](LICENSE.md) file for details

### References

* https://github.com/raspberrypi/pico-examples/tree/master/usb/device/dev_lowlevel
