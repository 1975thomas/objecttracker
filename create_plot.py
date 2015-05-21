#!/usr/bin/env python
# coding: utf-8
import os
__doc__ = """


Usage:
    {filename} [options] [--verbose|--debug] [--date=<date>|(--date-from=<date> --date-to=<date>)]

Options:
    -h, --help                      This help message.
    -d, --debug                     Output a lot of info..
    -v, --verbose                   Output less less info.
    --log-filename=logfilename      Name of the log file.
    --plot-path=<path>              Where to save the tracks,
                                    [default: /data/plots
    --date-from=<date>              Date from. Format YYYY-MM-DD.
    --date-to=<date>                Date to. Not included. Format YYYY-MM-DD.
    --street=<street>               Street.
""".format(filename=os.path.basename(__file__))

import objecttracker
import logging
import time
import datetime
import objecttracker.database
import numpy as np
import matplotlib.pyplot as plt

# Define the logger
LOG = logging.getLogger(__name__)

if __name__ == "__main__":
    import docopt
    args = docopt.docopt(__doc__, version="1.0")

    if args["--debug"]:
        logging.basicConfig(filename=args["--log-filename"],
                            level=logging.DEBUG)
    elif args["--verbose"]:
        logging.basicConfig(filename=args["--log-filename"],
                            level=logging.INFO)
    else:
        logging.basicConfig(filename=args["--log-filename"],
                            level=logging.WARNING)
    LOG.info(args)

    if args['--date'] is not None:
        date_from = datetime.datetime.strptime(args['--date'], "%Y-%m-%d")
    elif args['--date-from'] is not None:
        date_from = datetime.datetime.strptime(args['--date-from'], "%Y-%m-%d")
    else:
        date_from = datetime.datetime.now()

    if args['--date-to'] is not None:
        date_to = datetime.datetime.strptime(args['--date-to'], "%Y-%m-%d")
    else:
        date_to = date_from + datetime.timedelta(days=1)

    size_ranges = (0, 1000, 15000, 1000000)
    colors = ("c", "m", "y")
    labels = ("S", "M", "L")
    hour_range = ("07", "19")
        
    sql = "SELECT strftime('%Y-%m-%dT%H', date), strftime('%H', date), COUNT() FROM tracks WHERE date BETWEEN ? AND ? AND avg_size BETWEEN ? AND ? AND strftime('%H', date) BETWEEN ? AND ? GROUP BY strftime('%Y-%m-%dT%H', date);"

    with objecttracker.database.Db() as db:
        LOG.debug("Getting data from db.")
        x_min = int(hour_range[0])
        x_max = int(hour_range[1])
        ticks = ["%02i"%i for i in range(x_min, x_max+1)]
        plt.xlim(xmin=x_min, xmax=x_max)
        plt.xticks(range(x_min, x_max+1), ticks, rotation=30)

        title = "%s"%(date_from.strftime("%Y-%m-%d"))
        if (date_from - date_to).days > 1:
            title += " - %s"%(date_to.strftime("%Y-%m-%d"))
        if args['--street'] is not None:
            title = "%s %s"%(args['--street'], title)
        plt.title(title)

        plt.xlabel("Time")
        plt.ylabel("Antal")

        numbers = {}

        for i, size_range in enumerate(zip(size_ranges[0:], size_ranges[1:])):
            sql_values = (date_from, date_to, size_range[0], size_range[1], hour_range[0], hour_range[1])
            numbers[i] = []

            for row in db.get_rows(sql, sql_values):
                d, h, n = row
                numbers[i].extend([int(h),] * n)

        plt.hist(numbers.values(), bins=x_max+-x_min, range=(x_min, x_max), color=colors, label=labels, align='mid')

        plt.legend()
        plt.show()
