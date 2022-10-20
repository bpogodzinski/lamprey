from pprint import pprint as pp
import argparse
import logging
import os
import sys
from datetime import datetime
import bencoding
from lamprey.dataclass import Torrent
from lamprey.tracker import Tracker
from lamprey.common import check_user_disk_space

from lamprey.common import format_bytes
import urllib.parse

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
torrent = bencoding.bdecode(FILE)
size, postfix = format_bytes(torrent[b'info'][b'length'])
created_at = datetime.fromtimestamp(torrent[b'creation date'])
torrent_information = f"""

    name: {torrent[b'info'][b'name'].decode()}
    comment: {torrent[b'comment'].decode()}
    created: {created_at}
    size: {f'{size:.2f} {postfix}'}
    """

logging.info(torrent_information)
pp(torrent[b'announce'])
pp(torrent[b'announce-list'])
torrent_info = Torrent((torrent[b"comment"]), (torrent[b"created by"]), (datetime.fromtimestamp(torrent[b"creation date"])),  (
    torrent[b"url-list"]), (torrent[b"info"]), (torrent[b'info'][b'name']), (torrent[b'info'][b'length']), (torrent[b'info'][b'piece length']), (torrent[b'announce']), (torrent[b'announce-list']))
xd = Tracker(torrent_info)

xd._create_announce_url()

if args.dry_run:
    logging.warning("dry run, won't download")
    sys.exit(0)

# Check if user have enough space on the drive, assume that you download the file in the current directory
# check_user_disk_space()


# Extract info required to connect to the tracker

# Return data from tracker
