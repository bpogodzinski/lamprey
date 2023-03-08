import socket
from pprint import pprint as pp
import argparse
import logging
import os
from datetime import datetime
import bencoding
import struct
import bitstring
from lamprey.dataclass import Torrent, Have, Piece, Request, Cancel, Choke, KeepAlive, Bitfield, Interested, ID_to_msg_class
from lamprey.tracker import Tracker

from lamprey.common import format_bytes

class BufferMessageIterator:
    BUFFER_HEADER_LENGTH = 4
    def __init__(self, buffer, socket):
        self._buffer = buffer if buffer else b''
        self._socket = socket

    def __iter__(self):
        return self

    def __next__(self):
        while True:

            try:
                if len(self._buffer) < 4:
                    self._buffer += s.recv(10*1024)
                
                # jeśli bufor jest pusty to dorzuć kolejną paczkę danych z s.recv
                
                # sprawdź długość oraz id wiadomości
                # Co to za wiadomość
                message_length = struct.unpack('>I', self._buffer[0:4])[0]
                message_id = struct.unpack('>b', self._buffer[4:5])[0] if message_length > 0 else None
                
                # co to jest za wiadomość (z id wiadomości chce mieć klase wiadomości)
                # jeśli wiadomość ma ze sobą payload to chce dostać surowe dane TCP i je zdekodować w odpowiedniej
                # klasie za pomocą Nazwa_klasy.decode(dane_binarne)
                logging.debug(f'''
                    Message from: {peer}
                    Message length: {message_length}
                    Message ID: {message_id} {ID_to_msg_class[message_id]}
                ''')
                
                if message_length == 0:
                    return KeepAlive()
                
                print(f"buffor przed usunięciem: {self._buffer.hex(' ')}")
                # Messages with payload
                if message_id in [Bitfield.ID, Have.ID, Piece.ID, Request.ID, Cancel.ID]:
                    peer_message = self._buffer[:message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH]
                    # usuń pobrane dane z bufora
                    self._buffer = self._buffer[message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH:]
                    print(f"buffor po usunięciu: {self._buffer.hex(' ')}")
                    return ID_to_msg_class[message_id].decode(peer_message)
                # Messages without payload
                else:
                    self._buffer = self._buffer[BufferMessageIterator.BUFFER_HEADER_LENGTH + message_length:]
                    print(f"buffor po usunięciu: {self._buffer.hex(' ')}")
                    return ID_to_msg_class[message_id]()
                    # jeśli zła wiadomość to stop iteration
                    raise StopIteration()
            # TODO: Implementacja StopIteration w naszym iteratorze
            except XYZ as e:
                pass


            

def handshake(peer) -> bool:
    handshake_format = '!B19s8x20s20s'

    logging.debug(f'Handshake attempt to {peer}:{port}')
    message = struct.pack(handshake_format, 19, 'BitTorrent protocol'.encode('utf-8'),
                          tracker.info_hash, tracker.peer_id.encode('utf-8'))
    s.sendall(message)
    handshake_data = s.recv(68)
    if len(handshake_data) < 68:
        logging.debug(f'Handshake attempt to {peer}:{port} failed: Invalid handshake response')
        return False
    peer_response = struct.unpack(handshake_format, handshake_data)
    if peer_response[2] != tracker.info_hash:
        logging.error('Peer does not have the same infohash')
        exit(1) # Something wrong with tracker, not important right now and rarely happens
    logging.debug(
            f'Handshake recevied from {peer}:{port}\n{peer_response}')
    return True

# TODO: Zapisuj stan połączenia
# >Each client starts in the state choked and not interested.
# >That means that the client is not allowed to request pieces from the remote peer,
# >nor do we have intent of being interested.

# Choked A choked peer is not allowed to request any pieces from the other peer.
# Unchoked A unchoked peer is allowed to request pieces from the other peer.
# Interested Indicates that a peer is interested in requesting pieces.
# Not interested Indicates that the peer is not interested in requesting pieces.

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

        # Setup connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((peer, port))
        s.settimeout(None)

        # Initiate connection with peer
        
        # TODO, dac 5 prob połączenia handshake 
        for i in range(5):
            success = handshake(peer)
            logging.debug(f'Handshake attempt {i+1}: {"Success" if success else "Failed"}')
            if success:
                break
        if not success:
            logging.debug(f'5 Handshake attempts were failed, skipping peer')
            continue


        # Get the peer responce and decode
        # the lenght and the type of the message
        # peer_response = s.recv(10*1024)
        for message in BufferMessageIterator([], s):
            pass
            

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
        msg = Interested()
        s.sendall(msg.encode())
        logging.debug(f'Sending interested message to: {peer}')

    except OSError as e:
        logging.debug(f'Connection to {peer}:{port} closed: {e}')
        s.close()
        continue


'''
1. A torrents data is split into N number of pieces of equal size (except the last piece in a torrent, which might be of smaller size than the others)

2. The piece length is specified in the .torrent file. Typically pieces are of sizes 512 kB or less, and should be a power of 2.

N - ilość pieces == bitfield

czyli N * piece length >= długość całego torrenta
N >= długość torrenta / piece length

https://stackoverflow.com/questions/44308457/confusion-around-bitfield-torrent - size of bitfield

Yes, in the BitTorrent protocol, the bitfield message sent between peers is constant for a given torrent file. The length of the bitfield message is determined by the number of pieces in the torrent file, and this value is the same for all peers sharing the same torrent.

Each bit in the bitfield corresponds to a piece in the torrent file, and the value of the bit indicates whether the peer has that piece or not. So, if two peers are sharing the same torrent file, they should have the same length bitfield and the same set of bits indicating which pieces they have.

However, it's worth noting that not all peers will have the complete set of pieces for a given torrent file. Peers may join or leave the swarm at different times, and some may have slower download speeds or limited storage capacity, which can affect which pieces they have available. So, while the length of the bitfield message is constant, the specific set of pieces indicated by each peer may differ.

Progress:

Zapisuj odebrane dane z s.recv do bufora, czytaj je po kolei.
Przekazuj bufor dalej
def parse(self):
https://github.com/eliasson/pieces/blob/500c833cd3360c8d605376f73a5e79bb03781b57/pieces/protocol.py#L248
'''