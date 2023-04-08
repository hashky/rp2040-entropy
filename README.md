# RP2040 hardware random number generator


This is a fork of a previous modification fo pico_rng by polhenarejos

Changes include:
* driver updated, added included headers that were preventing my system from compiling it
* driver modified so that it presents the devnode fs object with permissins 0644 so that users can read it
* the hashing function implemented in the firmware was done incorrectly, updating in 64 bit blocks when specs have it at 8 bits/1byte per round.  fixed this to follow specs. 
* some entropy from the ADC connected to the temperature sensor integral to the RP2040, providing another source of physical entropy
* speed improvement removing some redundancy, resulting in 2x speed improvement of entropy produced
* organized the test scripts a little better
* 

##prerequisites
* linux headers for your kernel
* pico sdk, add it to your path like below

```bash
sudo apt install linux-headers-generic
git clone https://github.com/raspberrypi/pico-sdk
cd pico-sdk
git submodule update --init  --recursive
export PICO_SDK_PATH=`pwd`
echo "export PICO_SDK_PATH=`pwd`" >> .bashrc 
#^ adds the pico SDK to path to your environment in your shell pemanently where cmake on projects like this can find it
apt install dieharder 
#optionally if you are modifying it and want to run the industry standard battery of tests
```

## build fw
```bash
mkdir build
cd build
cmake ..
make
```

## upload fw
```bash
cp build/firmware/pico_rng.uf2 /media/$USER/RPI-RP2
```

##build driver
```bash
cd driver
mkdir build
cd build
cmake ..
make
```

##load up driver
```bash
sudo insmod driver/pico_rng.ko [debug=1] [timeout=<msec timeout>]
```

##run basic tests
```bash
test/tests.sh
```

##run extensive benchmark on quality of produced entropy
```bash
apt install dieharder
test/pico_rng_test.py --size 1073741824 > sample.rng
dieharder -a -g 201 -k 2 -Y 1 -m 2 -f sample.rng
```
this takes a long time. if you are trying to improve the codebase it must pass this test as well or better than previous code. the diehard(er) battery of tests are the industry standard for testing quality of entropy. something is only random if it has no deterministic process behind it. Randomness we use IRL is also evenly distributed in its domain if otherwise unspecified. 

You can not prove the absence of an underlying deterministic process from the raw data samples alone, so the best way to attempt to check if some data is actually random is to conduct a laundry list of statistical tests that attempt to show that the data is not random. This attempts to demonstrate that even with exhaustive effort, you can not establish the data as having any redundancy necessary for it to be the result of a deterministic process. A deterministic process necessarily has a finite number of operations that define it, and finite information in its initial conditions. Which means that given enough time/samples/iterations, it will have to express some redundant behavior that statistical methods can pick up on. It will essentially run out of new information(entropy) to express, so some form of redundancy will manifest. It requires an infinite amount of data to establish that no such finite deterministic process is the source of said data, so we have to settle for a few gigabytes. The diehard tests seem to want a terabyte or so and will wrap around smaller sets and tell you how many



