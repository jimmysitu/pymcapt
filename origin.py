#!/usr/bin/python2

from optparse import OptionParser
import mcpat


if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("--infile", dest="infile",
                    help="input file name" )
    parser.add_option("--print_level", dest="plevel", default=2,
                    help="level of details 0~5")
    parser.add_option("--opt_for_clk", dest="opt_for_clk", default=1,
                      help="0:optimize for ED^2P only, 1:optimzed for target clock rate")

    (opts, args) = parser.parse_args()

    mcpat.cvar.opt_for_clk = bool(opts.opt_for_clk)

    p1 = mcpat.ParseXML()
    p1.parse(opts.infile)

    proc = mcpat.Processor(p1)
    proc.displayEnergy(2, opts.plevel)

    exit(0)
