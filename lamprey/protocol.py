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
            f'Handshake recevied from {s.getpeername()}\n{peer_response}')
    return True

class BufferMessageIterator:
    BUFFER_HEADER_LENGTH = 4
    def __init__(self, main_socket: socket.socket):
        self._socket = main_socket
        self._buffer = b''

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                if len(self._buffer) < 4:
                    self._buffer += self._socket.recv(10*1024)
                logging.debug(f'Buffor on start {self._buffer.hex(" ")}')

                # sprawdź długość oraz id wiadomości
                # Co to za wiadomość
                message_length = struct.unpack('>I', self._buffer[0:4])[0]
                message_id = struct.unpack('>b', self._buffer[4:5])[0] if message_length > 0 else None
                
                # co to jest za wiadomość (z id wiadomości chce mieć klase wiadomości)
                # jeśli wiadomość ma ze sobą payload to chce dostać surowe dane TCP i je zdekodować w odpowiedniej
                # klasie za pomocą Nazwa_klasy.decode(dane_binarne)
                logging.debug(f'''
                    Message from: {self._socket.getpeername()}
                    Message length: {message_length}
                    Message ID: {message_id} {ID_to_msg_class[message_id]}
                ''')
                
                if message_length == 0:
                    # Usuń buffor by zapobiec keep-alive loop
                    self._buffer = self._buffer[BufferMessageIterator.BUFFER_HEADER_LENGTH:]
                    return KeepAlive()
                
                # Messages with payload
                if message_id in [Bitfield.ID, Have.ID, Piece.ID, Request.ID, Cancel.ID]:
                    buffer_size = len(self._buffer)
                    peer_message = self._buffer[:message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH]
                    peer_message_len = len(peer_message)
                    
                    # Get the rest of the data from socket if extracted message is shorter than expected
                    if peer_message_len < message_length:
                        logging.warning(f'Buffor size is len {buffer_size} and the message is len {message_length}, Getting the rest of the data from socket')
                        # Get the rest of missing data to buffer
                        bytes_to_download = message_length - peer_message_len + BufferMessageIterator.BUFFER_HEADER_LENGTH
                        self._buffer += self._socket.recv(bytes_to_download)
                        logging.warning(f'Buffer after recv {self._buffer.hex(" ")}')
                        peer_message += self._buffer[:message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH]
                    
                    # Delete last message from buffer
                    self._buffer = self._buffer[message_length + BufferMessageIterator.BUFFER_HEADER_LENGTH:]
                    logging.debug(f'Buffer after data consumption {self._buffer.hex(" ")}')
                    return ID_to_msg_class[message_id].decode(peer_message)
                
                # Messages without payload
                else:
                    self._buffer = self._buffer[BufferMessageIterator.BUFFER_HEADER_LENGTH + message_length:]
                    return ID_to_msg_class[message_id]()
            except KeyError:
                logging.error(f'Unknown message ID: {message_id}')
                raise StopIteration
            except socket.timeout:
                logging.debug(f'Peer timeout after {self._socket.gettimeout()} seconds')
                raise StopIteration