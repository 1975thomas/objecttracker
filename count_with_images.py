#!/usr/bin/env python
# coding: utf-8
import os
__doc__ = """Usage:
    {filename} [options] <image_directory> [--verbose|--debug]

Options:
    -h, --help                        This help message.
    -d, --debug                       Output a lot of info..
    -v, --verbose                     Output less less info.
    --log-filename=logfilename        Name of the log file.
""".format(filename=os.path.basename(__file__))

import time
from collections import deque
import cv2
import numpy as np
import objecttracker

import logging
# Define the logger
LOG = logging.getLogger(__name__)

import docopt
args = docopt.docopt(__doc__, version="1.0")

if args["--debug"]:
    logging.basicConfig(filename=args["--log-filename"], level=logging.DEBUG)
elif args["--verbose"]:
    logging.basicConfig(filename=args["--log-filename"], level=logging.INFO)
else:
    logging.basicConfig(filename=args["--log-filename"], level=logging.WARNING)
LOG.info(args)

def get_images_frompath(path):
    for root, dirs, files in os.walk(path):
        files.sort()
        for filename in files:
            if filename.endswith(".png"):
                LOG.debug("Filename: %s"%os.path.join(root, filename))
                yield cv2.imread(os.path.join(root, filename))

def start_counting(image_directory):
    fgbg = cv2.BackgroundSubtractorMOG()

    resolution = (640/2, 480/2)
    track_match_radius = max(resolution)/4

    tracks = []
    for frame in get_images_frompath(image_directory):
        trackpoints = objecttracker.get_trackpoints(frame, fgbg)
        tracks, tracks_to_save = objecttracker.get_tracks(trackpoints, tracks, track_match_radius)

        frame_width = frame.shape[0]
        min_linear_length = 0.5*frame_width
        for t in tracks_to_save: t.save(min_linear_length)

        # Draw.
        objecttracker.draw_tracks(tracks, frame)

        cv2.imshow("RESULT frame", frame)

        if len(tracks) + len(tracks_to_save) > 0:
            time.sleep(1/5.0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print "FIN"
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_counting(args['<image_directory>'])