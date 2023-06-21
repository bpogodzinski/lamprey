class Block:
    def __init__(self, size = 2**14, content = None, index = None, piece = None, is_completed = False, is_downloading = False):
        self.size = size
        self.content = content
        self.index = index
        self.piece = piece
        self.is_completed = is_completed
        self.is_downloading = is_downloading



        self.file_begin =  size = 0
        self.file_end = size= 2*14

    

        self.expected_shasum = None

blok = Block(300)

print(blok.size)

# class Piece:
#     def __init__(self, size, block_list = None, index = None, is_completed = False, is_downloading = False):
#         self.size = size
#         self.block_list = block_list
#         self.index = index
#         self.is_completed = is_completed
#         self.is_downloading = is_downloading

# # obiekt_piece = Piece(index=0)
# # obiekt_block = Block(index=0, content='xd', piece=obiekt_piece)

# obiekt_piece = Piece(index=0)
# obiekt_piece.block_list.append(Block(index=0))

# obiekt_piece = Piece() # Nie zadziała
# obiekt_piece = Piece(10) # Zadziała
# obiekt_piece = Piece(size=10) #Zadziała
# obiekt_piece = Piece(10, index=0) #Zadziała
# obiekt_piece = Piece(index=0, 10) # Nie zadziała
# obiekt_piece = Piece(10,[],is_completed=False, index=0)
# # obiekt_block = Block(index=0, content='xd', piece=obiekt_piece)