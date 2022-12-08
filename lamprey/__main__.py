import socket
from pprint import pprint as pp
import argparse
import logging
import os
import sys
from datetime import datetime
import requests
import bencoding
import struct
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
# pp(torrent[b'announce'])
# pp(torrent[b'announce-list'])
torrent_info = Torrent((torrent[b"comment"]), (torrent[b"created by"]), (datetime.fromtimestamp(torrent[b"creation date"])),  (
    torrent[b"url-list"]), (torrent[b"info"]), (torrent[b'info'][b'name']), (torrent[b'info'][b'length']), (torrent[b'info'][b'piece length']), (torrent[b'announce']), (torrent[b'announce-list']))
tracker = Tracker(torrent_info)
tracker_response = tracker.connect()
# 1. Zrób funkcje która przyjmuje content z odpowiedzi trackera i zwraca liste peerów
peers_list = []
offset = 6
peers = bencoding.bdecode(tracker_response.content)[b'peers']
if tracker_response.status_code == 200:
    number_of_peers = len(peers)//6
    for peer in range(0, number_of_peers):
        peers_list.append(
            f"{peers[0+offset+peer]}.{peers[1+offset+peer]}.{peers[2+offset+peer]}.{peers[3+offset+peer]}:{int.from_bytes(peers[4+offset+peer:6+offset+peer], byteorder='big')}")
# 2. Połącz się z każdym peerem i wyprintuj odpowiedź od niego

# The handshake is a required message and must be the first message transmitted by the client. It is (49+len(pstr)) bytes long.
# handshake: <pstrlen><pstr><reserved><info_hash><peer_id>

# Z = 19BitTorrent protocol00000000{tracker.info_hash}{tracker.peer_id}

# pstrlen: string length of < pstr >, as a single raw byte
# pstr: string identifier of the protocol
# reserved: eight(8) reserved bytes. All current implementations use all zeroes. Each bit in these bytes can be used to change the behavior of the protocol. An email from Bram suggests that trailing bits should be used first, so that leading bits may be used to change the meaning of trailing bits.
# info_hash: 20-byte SHA1 hash of the info key in the metainfo file. This is the same info_hash that is transmitted in tracker requests.
# peer_id: 20-byte string used as a unique ID for the client. This is usually the same peer_id that is transmitted in tracker requests(but not always e.g. an anonymity option in Azureus).

handshake_format = '!B19s8x20s20s'
message = struct.pack(handshake_format, 19, 'BitTorrent protocol'.encode('utf-8'),
                      tracker.info_hash, tracker.peer_id.encode('utf-8'))
assert len(message) == 68, 'Invalid message length'

# Handshake
single_peer = peers_list[0].split(':')
host = single_peer[0]
port = int(single_peer[1])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall(message)
data = s.recv(68)
s.close()
peer_response = struct.unpack(handshake_format, data)
print('Received', peer_response)
if peer_response[2] != tracker.info_hash:
    logging.warning('Peer does not have the same infohash')

# 2.1 odbierz wiadomość bitfield od peera

# 2.2 wyślij do peera wiadomość interested

# 2.3 odbierz od peera chocked/unchocked etc

if args.dry_run:
    logging.warning("dry run, won't download")
    sys.exit(0)

# Check if user have enough space on the drive, assume that you download the file in the current directory
# check_user_disk_space()


# Extract info required to connect to the tracker

# Return data from tracker
