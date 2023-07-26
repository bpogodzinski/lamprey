import logging
import struct
import socket
from .tracker import Tracker
from .dataclass import ID_to_msg_class, Have, Piece, Request, Cancel, Choke, KeepAlive, Bitfield, Interested

def handshake(s: socket.socket, tracker: Tracker) -> bool:
    handshake_format = '!B19s8x20s20s'
    logging.debug(f'Handshake attempt to {s.getpeername()}')
    message = struct.pack(handshake_format, 19, 'BitTorrent protocol'.encode('utf-8'),
                          tracker.info_hash, tracker.peer_id.encode('utf-8'))
    s.sendall(message)
    handshake_data = s.recv(68)
    if len(handshake_data) < 68:
        logging.debug(f'Handshake attempt to {s.getpeername()} failed: Invalid handshake response')
        return False
    peer_response = struct.unpack(handshake_format, handshake_data)
    if peer_response[2] != tracker.info_hash:
        logging.error('Peer does not have the same infohash')
        exit(1) # Something wrong with tracker, not important right now and rarely happens
    logging.debug(
            f'Handshake recevied from {s.getpeername()}')
    return True


# https://docs.python.org/3/howto/sockets.html
# https://code.activestatARG UDA_DIRe.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/
class PeerSocket():
    def __init__(self, peer_socket):
        self.socket = peer_socket

    def create_connection(address, timeout=10,
                      source_address=None, *, all_errors=False):
        return PeerSocket(socket.create_connection(address, timeout))


    def full_recv(self, total_data = None, n = 0) -> bytes:
        total_data = []
        bytes_recd = 0
        while bytes_recd < n:
            total_data = self.PeerSocket.recv(min(n - bytes_recd, 2048))
            if total_data == b'':
                raise RuntimeError("socket connection broken")
            total_data.append(total_data)
            bytes_recd = bytes_recd + len(total_data)
        return b''.join(total_data)
    
# Tworzyć połączenie z danym peerem
# W __pełni__ wysyłać i odbierać wiadomości o danej długości (np message_length otrzymany w recv lub długość naszej wiadomości przy send)
# Posiadać metody które zwrócą całą wiadomość od peera lub true jak wyślą w pełni wiadomość do peera
# W pełni otrzymane wiadomości będziemy pakować do self._buffer w BufferMessageIterator

class BufferMessageIterator:
    BUFFER_HEADER_LENGTH = 4
    def __init__(self, main_socket: socket.socket):
        self._socket = main_socket
        self._buffer = b''

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if len(self._buffer) < 4:
                self._buffer += self._socket.recv(10*1024)
            if len(self._buffer) >= 4:
                message_length = struct.unpack('>I', self._buffer[0:4])[0]
                message_id = struct.unpack('>b', self._buffer[4:5])[0] if message_length > 0 else None
                logging.debug(f'''
                    Message from: {self._socket.getpeername()}
                    Message length: {message_length}
                    Message ID: {message_id} {ID_to_msg_class[message_id]}
                ''')
                
                if message_length == 0:
                    self._buffer = self._buffer[BufferMessageIterator.BUFFER_HEADER_LENGTH:]
                    return KeepAlive()
                
                # Messages with payload
                if message_id in [Bitfield.ID, Have.ID, Piece.ID, Request.ID, Cancel.ID]:
                    buffer_size = len(self._buffer)
                    peer_message = self._buffer[:message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH]
                    peer_message_len = len(peer_message)
                    
                    # Get the rest of the data from socket if extracted message is shorter than expected
                    if peer_message_len < message_length:
                        logging.debug(f'Buffor size is len {buffer_size} and the message is len {message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH}, Getting the rest of the data from socket')
                        # Get the rest of missing data to buffer
                        bytes_to_download = message_length - peer_message_len + BufferMessageIterator.BUFFER_HEADER_LENGTH
                        self._buffer += self._socket.full_recv(bytes_to_download)
                        logging.debug(f'Buffer size after downloading data {len(self._buffer)}')
                        assert len(self._buffer) == message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH
                        peer_message += self._buffer[:message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH]
                    
                    # Delete last message from buffer
                    self._buffer = self._buffer[message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH:]
                    return ID_to_msg_class[message_id].decode(peer_message)
                
                # Messages without payload
                else:
                    self._buffer = self._buffer[BufferMessageIterator.BUFFER_HEADER_LENGTH + message_length:]
                    return ID_to_msg_class[message_id]()
            
            # No new messages from peer
            else:
                return None
                
        except KeyError:
            logging.error(f'Unknown message ID: {message_id}')
            raise StopIteration
        except socket.timeout:
            logging.debug(f'Peer timeout after {self._socket.gettimeout()} seconds')
            raise StopIteration