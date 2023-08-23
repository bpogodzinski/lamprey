import bitstring
from dataclass import Torrent

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
    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        self.bitfield = self.create_bitfield()
        self.peer_bitfield = None
    
    def create_bitfield(self):
        return bitstring.BitArray(auto=[False for _ in range(self.torrent.get_number_of_pieces())])

    def save_peer_bitfield(self, bitfield):
        self.peer_bitfield = bitfield

    def request_piece(self, ...):
        # Find first available piece to download
        # send request to peer
        raise NotImplementedError
        REQUEST_SIZE = 2**14
        index = 0
        s.sendall(Request(index, 0, REQUEST_SIZE).encode())

    def process_have_message(self, ...):
        # Process have message, fill 1 in place of 0
        # in bitfield
        raise NotImplementedError
    
    def save_piece(self, file_data):
        pass

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