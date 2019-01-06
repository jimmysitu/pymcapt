#!/usr/bin/python3 -u

from optparse import OptionParser
import matplotlib.pyplot as plt
import re

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-p", "--power", dest="pwr",
                    help="Power log file from mcpat")

    (opts, args) = parser.parse_args()
    fp = open(opts.pwr, 'r')

    powerStats = []
    line = fp.readline()
    while(line):
        m = re.match(r'^  Runtime Dynamic = (\S+) W', line)
        if m:
            powerStats.append(float(m.group(1)))
        line = fp.readline()

    fp.close()
    print(powerStats)
    plt.plot(powerStats)
    plt.xlabel("Time(ms)")
    plt.ylabel("Power(W)")
    plt.show()
    exit(0)
