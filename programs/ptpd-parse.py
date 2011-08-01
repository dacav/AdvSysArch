#!/usr/bin/env python

from __future__ import print_function, division
import sys
import itertools
import dateutil.parser as parsedate
import csv
import pylab

try: range = xrange
except: pass

TIME_FORMAT = ["%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S"]

class PTPStat :

    def __init__ (self, time, owd, off_mast, s2m, m2s, drift):
        self.time = time
        self.one_way_delay = owd
        self.offset_from_master = off_mast
        self.slave_to_master = s2m
        self.master_to_slave = m2s
        self.drift = drift

def iter_steps (csv):
    to_time = lambda s : parsedate.parse(
                            "{0}.{2}".format(*s.rpartition(':'))
                         )
    def tuple_parts (row):
        fields = itertools.imap( lambda s : s.strip(), row )
        try:
            ts = to_time(next(fields))
            if next(fields) != 'slv': raise Exception
            yield True
            yield ts
            next(fields)
            for oth in fields: yield float(oth)
        except Exception, msg:
            # Invalid row detected
            print("Skipping \"{0}\" ({1})".format(",".join(row), msg))
            yield False
    csv = itertools.imap(tuple_parts, csv)
    csv = itertools.ifilter( lambda tp : next(tp), csv )
    return itertools.starmap(PTPStat, csv)

def plot (gen):
    xs = list(ev.time for ev in gen)

    ovds = list( ev.one_way_delay for ev in gen )
    ofms = list( ev.offset_from_master for ev in gen )
    s2ms = list( ev.slave_to_master for ev in gen )
    m2ss = list( ev.master_to_slave for ev in gen )
    drfts = list( ev.drift for ev in gen )

    items = list()

    pylab.figure(1)
    pylab.xticks(rotation=45, size='small')
    items.append( pylab.plot_date(xs, ovds, "c-") )
    items.append( pylab.plot_date(xs, ofms, "m-") )
    items.append( pylab.plot_date(xs, s2ms, "y-") )
    items.append( pylab.plot_date(xs, m2ss, "k-") )
    pylab.legend(items, ["One way delay",
                         "Offset from Master",
                         "Slave to Master",
                         "Master to Slave",])

    pylab.figure(2)
    pylab.xticks(rotation=45, size='small')
    pylab.legend([ pylab.plot_date(xs, drfts, "r-") ],
                 [ "Drifts" ])


    pylab.show()

def main (argv=None):
    if not argv: argv = sys.argv
    logfile = open(argv[1])
    gen = list( iter_steps(csv.reader(logfile)) )
    plot(gen)
    logfile.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

