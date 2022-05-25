import argparse
import logging
import os

parser = argparse.ArgumentParser(
    prog="lamprey-cli", description="Lamprey BitTorrent client"
)

# positional arguments
parser.add_argument(
    "torrent-file",
    type=argparse.FileType('rb'),
    help=".torrent file to download"
)

# optional arguments
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    dest="verbosity",
    default=0,
    help="increase verbosity (default: print warnings, errors)"
)

args = parser.parse_args()
