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
        return f'index:{self.index} is_compl: {self.is_completed}'



bitfield = []

length = 1151975424
piece_length = 262144
number_of_pieces = 4395
blocks_in_piece = 16

for piece_index in range(number_of_pieces):
    blocks = []
    piece = Piece(index=piece_index, length=262144)
    for block_index in range(blocks_in_piece):
        blocks.append(Block(piece=piece))
    piece.block_list = blocks
    bitfield.append(piece)

print([str(x) for x in bitfield if x.index == 23])

# requestujemy bloki a nie piece
peer_socket.sendall(Request(x.index, x.begin, FileManager.REQUEST_SIZE).encode())


# znajdz piecey które mają przynajmiej jeden ściągnięty blok
[piece for piece in bitfield if any(block.is_completed for block in piece.block_list)]