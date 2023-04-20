#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy import stats

parser = argparse.ArgumentParser(
    description="Raspberry Pi Pico Random Number Generator Test Analyzer"
)
parser.add_argument(
    "file", help="File that contains a random sample of bytes.", metavar="FILENAME"
)
parser.add_argument("--save", action="store_true", help="save figs")
args = parser.parse_args()


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


with open(args.file, "rb") as f:
    myhist = np.zeros(256, dtype="float64")
    chisqs = []
    chisps = []
    acumd = 0
    acumn = 0
    for data in read_in_chunks(f, 10000):
        n, jnk = np.histogram(list(data), list(range(257)))
        myhist += n
        chisq, chisp = stats.chisquare(n)
        chisqs.append(chisq)
        chisps.append(chisp * 100)
        acumd += sum(data)
        acumn += len(data)

    #    plt.subplot(1, 2, 1)
    plt.bar(range(256), myhist / np.sum(myhist), width=1)
    plt.ylabel("Probability")
    plt.title(f"Distribution of randomness [$\mu$={acumd/acumn:.4f}]")
    plt.grid(True)
    if args.save:
        plt.savefig("figs/distrib.png")
        print("save figs/distrib.png")
        plt.close()
    else:
        plt.show()

    plt.subplot(1, 2, 1)
    n, bins, _ = plt.hist(chisqs, 401, density=True)
    plt.ylabel("Probability")
    plt.title(
        f"Distribution of chi-square [$\mu$={np.mean(chisqs):.4f}, Mdn={np.median(chisqs):.4f}]"
    )
    plt.grid(True)

    plt.subplot(1, 2, 2)
    n, bins, _ = plt.hist(chisps, list(range(101)), density=False)
    plt.ylabel("Probability")
    plt.title(
        f"Distribution of percentage excess [$\mu$={np.mean(chisps):.4f}, Mdn={np.median(chisps):.4f}]"
    )
    plt.grid(True)
    if args.save:
        plt.savefig("figs/chi.png")
        print("save figs/chi.png")
        plt.close()
    else:
        plt.show()
    plt.show()
