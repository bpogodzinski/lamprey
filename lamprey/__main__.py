import socket
from pprint import pprint as pp
import argparse
import logging
import os
from datetime import datetime
import bencoding
import bitstring
from lamprey.dataclass import Torrent, KeepAlive, Choke, Unchoke, Interested, Not_Interested, Have, Bitfield, Request, Piece, Cancel, Port
from lamprey.protocol import handshake, BufferMessageIterator, PeerSocket
from lamprey.tracker import Tracker
from lamprey.piece_manager import FileManager
import math


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
logging.debug(f'Length {torrent_info.get_length()}')
logging.debug(f'Piece length {torrent_info.get_piece_length()}')
number_of_pieces = torrent_info.get_length() / torrent_info.get_piece_length()
logging.debug(f'Number of pieces is {math.ceil(number_of_pieces)}')

def pieces_length():
    p_left_overs = number_of_pieces % 1
    p_rest = p_left_overs * torrent_info.get_piece_length()
    if p_rest == 0:
        return torrent_info.get_piece_length()
    else:
        return p_rest

logging.debug(f'Last pieces have {pieces_length()} bytes')

block_size = 2**14
number_of_blocks = torrent_info.get_piece_length() / block_size
logging.debug(f'Number of block in pieces is {math.ceil(number_of_blocks)}')

def blocks_length():
    b_left_overs = number_of_blocks % 1
    b_rest = b_left_overs * block_size
    if b_rest == 0:
        return block_size
    else:
        return b_rest
logging.debug(f'Last block of piece have {blocks_length()} bytes')


num_block_of_last_piece = pieces_length() / block_size
logging.debug(f'Block number of last piece is {math.ceil(num_block_of_last_piece)} ')

def last_block_of_last_piece():
    l_b_left_overs = num_block_of_last_piece % 1
    l_b_rest = l_b_left_overs * block_size
    if l_b_rest == 0:
        return block_size
    else:
        return l_b_rest
logging.debug(f'Last block of last piece got {math.ceil(last_block_of_last_piece())} bytes ')
logging.debug(f'Piece List {torrent_info.get_pieces_SHA1_list()[4394]}')
logging.debug(f'1st piece {torrent_info.get_pieces_SHA1_list()[0]}')

file_manager = FileManager(torrent_info)


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

logging.info(f'Possible peers ({len(peers_list)}): {peers_list}')

# file manager singleton

for peer in peers_list:
    try:
        fm = FileManager(torrent_info)
        list_peer = peer.split(':')
        peer = list_peer[0]
        if peer != "37.48.74.20":
            continue
        port = int(list_peer[1])
        keep_alive_counter=0
        recieved_bitfield = None

        s = PeerSocket.create_connection((peer, port), timeout=10)

        # Initiate connection with peer
        for i in range(5):
            success = handshake(s, tracker)
            logging.debug(f'Handshake attempt {i+1}: {"Success" if success else "Failed"}')
            if success:
                break
        if not success:
            logging.debug(f'5 Handshake attempts were failed, skipping peer')
            continue

        pieces_list = None
        # Get the peer responce and decode
        # the length and the type of the message
        for message in BufferMessageIterator(s):
            if isinstance(message, KeepAlive):
                keep_alive_counter += 1

            elif isinstance(message, Choke):
                # Can't download pieces from peer
                logging.debug(f'Recevied Choke message from {s.getpeername()}')
                state.add(Choke)
                if Unchoke in state:
                    logging.debug(f'{s.getpeername()} started choking')
                    state.remove(Unchoke)

            elif isinstance(message, Unchoke):
                # Can request pieces from peer
                logging.debug(f'Recevied Unchoke message from {s.getpeername()}')
                # Request first available piece

                
            elif isinstance(message, Interested):
                logging.debug(f'Recevied Interested message from {s.getpeername()}')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Not_Interested):
                logging.debug(f'Recevied Not_Interested message from {s.getpeername()}')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Have):
                logging.debug(f'Recevied Have message from {s.getpeername()}')
                file_manager.process_have_message(message.piece_index)

            elif isinstance(message, Bitfield):
                logging.debug(f'Recevied Bitfield message from {s.getpeername()}')
                file_manager.save_peer_bitfield(message.bitfield)
                s.sendall(Interested().encode())
                logging.debug(f'Sent Interested message to {s.getpeername()}')
                s.sendall(Choke().encode())
                logging.debug(f'Sent Choke message to {s.getpeername()}')
                file_manager.request_piece(s,0)

            elif isinstance(message, Request):
                logging.debug(f'Recevied Request message from {s.getpeername()}')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Piece):
                logging.debug(f'Recevied Piece message from {s.getpeername()}')
                # peer wysłał nam kawałek pliku (block!!!), zapisz go do file managera
                # poproś o kolejny kawałek
                file_manager.save_piece(message)
                file_manager.request_piece(s, message.index + 1)

            elif isinstance(message, Cancel):
                logging.debug(f'Recevied Cancel message from {s.getpeername()}')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Port):
                logging.debug(f'Recevied Port message from {s.getpeername()}')
                # nie robimy nic bo nie implementujemy DHT (jeszcze)
            
            # elif message is None:
            #     logging.debug(f'No new messages from {s.getpeername()}')
                


            # Timestep debug
          
                
            elif temp_flag == 3:
                temp_flag = 5
                # Send first piece request
                pieces_list = torrent_info.get_pieces_SHA1_list()[0]
                logging.debug(f'Sent Request message to {s.getpeername()}')

    except ConnectionRefusedError as e:
        logging.debug(f'Connection to {peer}:{port}: {e}')
        continue
    except TimeoutError as e:
        logging.debug(f'Connection to {peer}:{port}: {e}')
    except OSError as e:
        logging.debug(f'Connection to {peer}:{port}: {e}')
