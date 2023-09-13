import bitstring
import logging
from lamprey.dataclass import Torrent, ID_to_msg_class, Request
from lamprey.protocol import PeerSocket

class Block:
    def __init__(self, size = 2**14, content = None, piece = None, is_completed = False, is_downloading = False):
        self.size = size
        self.content = content
        self.piece = piece
        self.is_completed = is_completed
        self.is_downloading = is_downloading



        self.file_begin = None
        
        self.file_end = None

        self.expected_shasum = None
    
    def __str__(self) -> str:
        return f'size: {self.size} piece: {self.piece.index}'

class Piece:
    def __init__(self, length, block_list = None, index = None, is_completed = False, is_downloading = False):
        self.length = length
        self.block_list = block_list if block_list else []
        self.index = index
        self.is_completed = is_completed
        self.is_downloading = is_downloading

    def __str__(self) -> str:
        return ' '.join(str(block) for block in self.block_list)


#Singleton ?
class FileManager:
    REQUEST_SIZE = 2**14
    miejsce_do_bloków = []
    our_bitfield = []

    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        self.bitfield = self.create_bitfield()
        self.peer_bitfield = None
    
    def create_bitfield(self):
        for piece_index in range(self.torrent.get_number_of_pieces()):
            blocks = []
            piece = Piece(self.torrent.get_piece_length(), index=piece_index)
            return FileManager.our_bitfield.append(FileManager.miejsce_do_bloków)

    def save_peer_bitfield(self, bitfield):
        self.peer_bitfield = bitfield

    def request_piece(self, peer_socket, index = 0, begin = 0):
        # Find block to download
        # send request to peer
        logging.debug(f'Sending request to {peer_socket.getpeername()}, index: {index}, begin:{begin}, length:{FileManager.REQUEST_SIZE}')
        peer_socket.sendall(Request(index, begin, FileManager.REQUEST_SIZE).encode())

    def process_have_message(self):
        # Process have message, fill 1 in place of 0
        # in bitfield
        pass
    
    def save_piece(self, file_data):
        FileManager.miejsce_do_bloków.append(file_data)
        

        pass
# pobrać bloki jedengo piece następnie zapisać, i zweryfikować jego HASH 


# obiekt_piece = Piece(262144, index=0)
# obiekt_piece1 = Piece(262144, index=1)
# obiekt_piece.block_list.append(Block(piece=obiekt_piece))
# obiekt_piece.block_list.append(Block(piece=obiekt_piece))
# obiekt_piece.block_list.append(Block(piece=obiekt_piece))
# obiekt_piece1.block_list.append(Block(piece=obiekt_piece1))
# obiekt_piece1.block_list.append(Block(piece=obiekt_piece1))
# obiekt_piece1.block_list.append(Block(piece=obiekt_piece1))

# print(str(obiekt_piece))
# print(str(obiekt_piece1))

# obiekt_piece.block_list[0]

# 1. stwórz klase my socket która będzie high level interface do low-levelowych socketów, musimy pozbyć się problemu "niedoczytanych" danych
# 2. stwórz nasz bitfield (wypełniony 0)