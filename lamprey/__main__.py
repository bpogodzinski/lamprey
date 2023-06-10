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
logging.debug(f'Piece List {torrent_info.get_pieces()[4394]}')
logging.debug(f'1st block 1st piece {torrent_info.get_pieces()[0]}')

import struct

block_list = torrent_info.get_pieces()[0]
struct.unpack('>IIIIIIIIIIIIIIII', block_list)
# pierwszy_block_list = block_list / 16

logging.debug(f'Block list of 1st piece{block_list}')
# 07.06 notatki



# podgląd lowlewel jak to wygląda
piece_list = [] # number of pieces
piece_list.append(torrent_info.get_pieces()[0, 0, block_size]) # 1st block, 1st piece
logging.debug(f'Piece List {piece_list[0]}')
piece_list.append((0, block_size, block_size)) # 2nd block, 1st piece
piece_list.append((0, 2*block_size, block_size)) # 3rd block, 1st piece
piece_list.append((0, 3*block_size, block_size)) # 4th block, 1st piece
# .... 16 blocks later
piece_list.append((1, 0, block_size)) # 1st block, 2nd piece
piece_list.append((1, block_size, block_size)) # 2nd block, 2nd piece
piece_list.append((0, 2*block_size, block_size)) # 3rd block, 2nd piece
piece_list.append((0, 3*block_size, block_size)) # 4th block, 2nd piece
# .... number_of_pieces later
# .... be careful that the last piece last block is shorter than block_size

class Piece():
    def __init__(self) -> None:
        self.block_list = []
        self.index = None
        self.is_downloaded = False

class Block():
    def __init__(self, length = 2**14) -> None:
        self.start = None
        self.length = length
        self.is_downloaded = False
        self.data = None

xdd = Block()
kua = Block(15)

dx = Piece()
dx.block_list.append(xdd)
dx.block_list.append(kua)
# aż piece nie ma wszystkich bloków

dxx = Piece()
dxxx = Piece()
dxxxx = Piece()
file = [dxx, dxxx, dxxxx] # 4395 Pieces

# przykład dla 0 piece
for piece in file:
    for block in piece:
        block.download_data() # make_request
    
    import sha
    assert sha1(b''.join([block.data for block in piece.block_list])) == torrent_info.get_pieces()[0]

# Zrobić klase piece managera który bęzie zbierał info o piecach i blokach
# koniec notatek

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
        state = set()

        s = socket.create_connection((peer, port), timeout=10)

        # Initiate connection with peer
        for i in range(5):
            success = handshake(s, tracker)
            logging.debug(f'Handshake attempt {i+1}: {"Success" if success else "Failed"}')
            if success:
                break
        if not success:
            logging.debug(f'5 Handshake attempts were failed, skipping peer')
            continue

        state.add(Choke)


        import time
        temp_flag = 1
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
                state.add(Unchoke)
                if Choke in state:
                    logging.debug(f'{s.getpeername()} stopped choking')
                    state.remove(Choke)
                
            elif isinstance(message, Interested):
                logging.debug(f'Recevied Interested message from {s.getpeername()}')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Not_Interested):
                logging.debug(f'Recevied Not_Interested message from {s.getpeername()}')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Have):
                logging.debug(f'Recevied Have message from {s.getpeername()}')
                # peer mówi że ma ten kawałek pliku
                # zaaktualizować bitfield
                # recieved_bitfield[piece_index] = 1

            elif isinstance(message, Bitfield):
                logging.debug(f'Recevied Bitfield message from {s.getpeername()}')
                recieved_bitfield = message.bitfield

            elif isinstance(message, Request):
                logging.debug(f'Recevied Request message from {s.getpeername()}')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Piece):
                logging.debug(f'Recevied Piece message from {s.getpeername()} {message}')
                # peer wysłał nam kawałek pliku, zapisz go

            elif isinstance(message, Cancel):
                logging.debug(f'Recevied Cancel message from {s.getpeername()}')
                # nie robimy nic bo nie seedujemy

            elif isinstance(message, Port):
                logging.debug(f'Recevied Port message from {s.getpeername()}')
                # nie robimy nic bo nie implementujemy DHT (jeszcze)
            
            # Timestep debug
            if temp_flag == 1:
                temp_flag = 3
                s.sendall(Interested().encode())
                logging.debug(f'Sent Interested message to {s.getpeername()}')
                s.sendall(Choke().encode())
                logging.debug(f'Sent Choke message to {s.getpeername()}')
                
            elif temp_flag == 3:
                temp_flag = 5
                # Send first piece request
                pieces_list = torrent_info.get_pieces()[0]
                REQUEST_SIZE = 2**14
                index = 0
                s.sendall(Request(index, 0, 262144).encode())
                logging.debug(f'Sent Request message to {s.getpeername()}')

    except ConnectionRefusedError as e:
        logging.debug(f'Connection to {peer}:{port}: {e}')
        continue
    except TimeoutError as e:
        logging.debug(f'Connection to {peer}:{port}: {e}')
    except OSError as e:
        logging.debug(f'Connection to {peer}:{port}: {e}')
