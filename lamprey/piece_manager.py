import bitstring
import logging
from lamprey.dataclass import Torrent, ID_to_msg_class, Request
from lamprey.protocol import PeerSocket

class Block:
    def __init__(self, size = 2**14, content = None, owning_piece = None, begin = None):
        self.size = size
        self.piece_index = owning_piece.index
        self.content = content
        self.owning_piece = owning_piece

        self.begin = begin

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


class FileManager:
    
    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        self.bitfield = self.create_bitfield()
        self.peer_bitfield = None
    
    def create_bitfield(self):
        bitfield = []
        for piece_index in range(self.torrent.get_number_of_pieces()):
            piece = Piece(length=self.torrent.get_piece_length(), index=piece_index)
            blocks = []
            num_of_blocks_to_add = self.torrent.number_of_blocks()
            if piece_index == self.torrent.get_number_of_pieces() - 1:
                num_of_blocks_to_add = self.torrent.num_block_of_last_piece()
            
            for block_index in range(num_of_blocks_to_add):
                block_begin = block_index * Torrent.BLOCK_SIZE
                blocks.append(Block(owning_piece=piece, begin = block_begin)) # 0 - piece_length
            piece.block_list = blocks
            bitfield.append(piece)

        return bitfield
    
    def save_peer_bitfield(self, bitfield):
        self.peer_bitfield = bitfield

    def request_piece(self, peer_socket, index = 0, begin = 0, length = 2**14):
        # Find block to download
        # send request to peer
        logging.debug(f'Sending request to {peer_socket.getpeername()}, index: {index}, begin:{begin}, length:{length}')
        peer_socket.sendall(Request(index, begin, length).encode())

    def process_have_message(self):
        # Process have message, fill 1 in place of 0
        # in bitfield
        pass
    
    def save_piece(self, file_data):
        pass
    #     FileManager.miejsce_do_bloków.append(file_data)

    def job_queue(self):
        queue = []
        if self.bitfield:
            for piece in self.bitfield:
                for block in piece.block_list:
                    queue.append(block)
        return queue
