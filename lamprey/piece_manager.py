import bitstring
import logging
from lamprey.dataclass import Torrent, ID_to_msg_class, Request
from lamprey.protocol import PeerSocket

class Block:
    def __init__(self, size = 2**14, index=None, content = None, owning_piece = None, is_completed = False, is_downloading = False, begin = None, end = None):
        self.size = size
        self.index = index
        self.content = content
        self.owning_piece = owning_piece
        self.is_completed = is_completed
        self.is_downloading = is_downloading

        self.begin = begin #to ma sie cały czas zwiększać       
        self.end = end  # ostatni blok to 1151975424, ostatni blok w pierwszym piece bedzie 262144
    
    def __str__(self) -> str:
        return f'size: {self.size} piece: {self.owning_piece.index}'


class Piece:
    def __init__(self, length, block_list = None, index = None, is_completed = False, is_downloading = False, expected_shasum = None):
        self.length = length
        self.block_list = block_list if block_list else []
        self.index = index
        self.is_completed = is_completed
        self.is_downloading = is_downloading
        self.expected_shasum = expected_shasum


    def __str__(self) -> str:
        return ' '.join(str(block) for block in self.block_list)


#Singleton ?
class FileManager:
    REQUEST_SIZE = 2**14
    
    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        self.bitfield = self.create_bitfield()
        self.peer_bitfield = None
    
    def create_bitfield(self):
        bitfield = []
        for piece_index in range(self.torrent.get_number_of_pieces()):
            piece = Piece(self.torrent.get_piece_length(), index=piece_index)
            blocks = []
            num_of_blocks_to_add = self.torrent.number_of_blocks()
            if piece_index == self.torrent.get_number_of_pieces() - 1:
                num_of_blocks_to_add = self.torrent.num_block_of_last_piece()
            
            for block_index in range(num_of_blocks_to_add):
                block_begin = self.file_begin_function(piece_index, block_index, FileManager.REQUEST_SIZE)
                block_end = self.file_end_function(block_begin, FileManager.REQUEST_SIZE, piece_index, block_index)
                blocks.append(Block(index=block_index, owning_piece=piece, begin = block_begin, end = block_end))
            piece.block_list = blocks
            bitfield.append(piece)

        return bitfield
    
    def file_begin_function(self, piece_index, block_index, size):
        if piece_index == 0:
            total_block_index = block_index
        if piece_index == 1 and block_index == 0:
            total_block_index = piece_index * self.torrent.number_of_blocks()
            begin = total_block_index * FileManager.REQUEST_SIZE
        if piece_index == self.torrent.get_number_of_pieces() and block_index == self.torrent.num_block_of_last_piece():
            begin = self.torrent.last_block_of_last_piece()
        else:
            total_block_index = piece_index * self.torrent.number_of_blocks()
            begin = (total_block_index + block_index) * FileManager.REQUEST_SIZE
        
        return begin      
        
        # return (piece_index + self.torrent.number_of_blocks) * size

    def file_end_function(self, file_begin, size, piece_index, block_index):
        if (piece_index == self.torrent.get_number_of_pieces() - 1) \
            and (block_index == self.torrent.num_block_of_last_piece() - 1) :
            return self.torrent.get_length()
        else:
            return file_begin + size - 1

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