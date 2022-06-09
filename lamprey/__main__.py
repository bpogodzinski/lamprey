import argparse
import logging
import os
import sys
from datetime import datetime
import bencoder
from dataclasses import Torrent

from lamprey.common import format_bytes
parser = argparse.ArgumentParser(
    prog="lamprey-cli", description="Lamprey BitTorrent client"
)

# positional arguments
parser.add_argument(
    "input_file",
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
parser.add_argument(
    "--dry-run",
    help="don't download anything",
    action="store_true",
)

args = parser.parse_args()

# set up logging
#
# -v for INFO
# -vv for DEBUG
log_level = max(logging.WARNING - 10 * args.verbosity, logging.DEBUG)
assert log_level <= logging.WARNING
assert log_level >= logging.DEBUG
logging.basicConfig(
    style="{",
    format="{asctime:} {name:30} {levelname:8} {message:}",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=log_level
)

logging.info("lamprey-cli PID=%d", os.getpid())

FILE = None
with args.input_file as file_reader:
    FILE = file_reader.read()

# Parse file
torrent = bencoder.decode(FILE)
size, postfix = format_bytes(torrent[b'info'][b'length'])
created_at = datetime.fromtimestamp(torrent[b'creation date'])
torrent_information = f"""

    name: {torrent[b'info'][b'name'].decode()}
    comment: {torrent[b'comment'].decode()}
    created: {created_at}
    size: {f'{size:.2f} {postfix}'}
    """

logging.info(torrent_information)


f = open("/home/pbartosz/lamprey-cli/archlinux-2022.05.01-x86_64.iso.torrent", "rb")
d = bencoder.decode(f.read())

t1 = Torrent((d[b"comment"]), (d[b"created by"]), (datetime.fromtimestamp(d[b"creation date"])), (d[b"url-list"]), (d[b"info"]), (d[b'info'][b'name']), (d[b'info'][b'length']), (d[b'info'][b'piece length']))

print(t1.get_comment())
print(t1.get_created_by())
print(t1.get_creation_date())
print(t1.get_url_list())
print(t1.get_info())
print(t1.get_name())
print(t1.get_length())
print(t1.get_piece_length())

if args.dry_run:
    logging.warning("dry run, won't download")
    sys.exit(0)

# Check if user have enough space on the drive

# Extract info required to connect to the tracker

# Return data from tracker
