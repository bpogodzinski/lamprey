import socket
from pprint import pprint as pp
import argparse
import logging
import os
from datetime import datetime
import bencoding
import bitstring
from lamprey.dataclass import Torrent, KeepAlive, Choke, Unchoke, Interested, Not_Interested, Have, Bitfield, Request, Piece, Cancel, Port
from lamprey.protocol import handshake, BufferMessageIterator
from lamprey.tracker import Tracker

from lamprey.common import format_bytes, check_user_disk_space

# TODO: Zapisuj stan połączenia
# >Each client starts in the state choked and not interested.
# >That means that the client is not allowed to request pieces from the remote peer,
# >nor do we have intent of being interested.

# Choked A choked peer is not allowed to request any pieces from the other peer.
# Unchoked A unchoked peer is allowed to request pieces from the other peer.
# Interested Indicates that a peer is interested in requesting pieces.
# Not interested Indicates that the peer is not interested in requesting pieces.

# state = []
# state.append(KeepAlive)
# state.append(Bitfield)

# TODO: Sprawdź czy użytkownik ma odpowiednio dużo przestrzeni dyskowej na plik
# Sprawdź pojemność dysku na który wskazuje path
# Check if user have enough space on the drive, assume that you download the file in the current directory
# check_user_disk_space()

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

logging.debug("lamprey-cli PID=%d", os.getpid())

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

torrent_info = Torrent((torrent[b"comment"]), (torrent[b"created by"]), (datetime.fromtimestamp(torrent[b"creation date"])),  (
    torrent[b"url-list"]), (torrent[b"info"]), (torrent[b'info'][b'name']), (torrent[b'info'][b'length']), (torrent[b'info'][b'piece length']), (torrent[b'announce']), (torrent[b'announce-list']))

tracker = Tracker(torrent_info)
tracker_response = tracker.connect()
peers_list = []
offset = 6

if tracker_response.status_code != 200:
    logging.error(f'Tracker returned non 200 code')
    exit(1)
peers = bencoding.bdecode(tracker_response.content)[b'peers']
number_of_peers = len(peers)//6

for peer in range(0, number_of_peers):
    peers_list.append(
        f"{peers[0+offset*peer]}.{peers[1+offset*peer]}.{peers[2+offset*peer]}.{peers[3+offset*peer]}:{int.from_bytes(peers[4+offset*peer:6+offset*peer], byteorder='big')}")

logging.info(f'Active peers ({len(peers_list)}): {peers_list}')

for peer in peers_list:
    try:
        list_peer = peer.split(':')
        peer = list_peer[0]
        port = int(list_peer[1])
        keep_alive_counter=0
        recieved_bitfield = None
        state = []

        s = socket.create_connection((peer, port), timeout=5)

        # Initiate connection with peer
        for i in range(5):
            success = handshake(s, tracker)
            logging.debug(f'Handshake attempt {i+1}: {"Success" if success else "Failed"}')
            if success:
                break
        if not success:
            logging.debug(f'5 Handshake attempts were failed, skipping peer')
            continue

        state.append(Choke)

        
        # Get the peer responce and decode
        # the length and the type of the message
        for message in BufferMessageIterator(s):
            if isinstance(message, KeepAlive):
                keep_alive_counter += 1

            elif isinstance(message, Choke):
                logging.debug('Got choke message')

            elif isinstance(message, Unchoke):
                logging.debug('Got Unchoke message')
                # skoro unchoke to wyślij interested

            elif isinstance(message, Interested):
                logging.debug('Got Interested message')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Not_Interested):
                logging.debug('Got Not_Interested message')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Have):
                logging.debug('Got Have message')
                # peer mówi że ma ten kawałek pliku
                # zaaktualizować bitfield
                # recieved_bitfield[piece_index] = 1

            elif isinstance(message, Bitfield):
                logging.debug('Got Bitfield message')
                recieved_bitfield = message.bitfield

            elif isinstance(message, Request):
                logging.debug('Got Request message')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Piece):
                logging.debug('Got Piece message')
                # peer wysłał nam kawałek pliku, zapisz go

            elif isinstance(message, Cancel):
                logging.debug('Got Cancel message')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Port):
                logging.debug('Got Port message')
                # nie robimy nic bo nie implementujemy DHT (jeszcze)

                              
            
            


        # message_length = struct.unpack('>I', peer_response[0:4])[0]
        # message_id = struct.unpack('>b', peer_response[4:5])[0] if message_length > 0 else None
        # message_payload = None
        # if message_id == 5:
        #     message_payload = bitstring.BitArray(peer_response[5:message_length]).bin
        # logging.debug(f'''
        #     Message from: {peer}
        #     Message length: {message_length}
        #     Message ID: {message_id} {ID_to_msg_class[message_id]}
        #     Message payload: {message_payload}
        #     ''')

        # Inform peer that we are interested in downloading pieces
        # msg = Interested()
        # s.sendall(msg.encode())
        # logging.debug(f'Sending interested message to: {peer}')

    except ConnectionRefusedError as e:
        logging.debug(f'Connection to {peer}:{port}: {e}')
        continue
    except TimeoutError as e:
        logging.debug(f'Connection to {peer}:{port}: {e}')
        continue
