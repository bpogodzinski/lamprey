from math import ceil
import struct
import bitstring

#  wrzucić wszystkie działania na pliku ( dzielenie pieców na bloki)

class Torrent():
    block_size = 2**14

    def __init__(self, comment, created_by, creation_date,
                 url_list, info, name, length, piece_length, announce, announce_list):
        self.comment = comment
        self.created_by = created_by
        self.creation_date = creation_date
        self.url_list = url_list
        self.info = info
        self.name = name
        self.length = length
        self.piece_length = piece_length
        self.announce = announce
        self.announce_list = announce_list

    def get_comment(self):
        return self.comment

    def get_created_by(self):
        return self.created_by

    def get_creation_date(self):
        return self.creation_date

    def get_url_list(self):
        return self.url_list

    def get_info(self):
        return self.info

    def get_name(self):
        return self.name

    def get_length(self):
        return self.length

    def get_piece_length(self):
        return self.piece_length

    def get_announce(self):
        return self.announce

    def get_announce_list(self):
        return self.announce_list
    
    def get_number_of_pieces(self):
        return ceil(self.get_length() / self.get_piece_length())
    
    def get_pieces_SHA1_list(self) -> list:
        pieces = self.info[b'pieces']
        byte_array = []
        while len(pieces) > 0:
            if len(pieces) >= 20:
                byte_array.append(pieces[:20])
                pieces = pieces[20:]
            else:
                byte_array.append(pieces)
        return byte_array
    
    def number_of_pieces(self):
        return self.length / self.piece_length


    def last_piece_length(self):
        number_of_pieces = self.length / self.piece_length
        
        p_left_overs = number_of_pieces % 1
        p_rest = p_left_overs * self.piece_length
        if p_rest == 0:
            return self.piece_length
        else:
            return p_rest


    def number_of_block(self):
        return self.piece_length / Torrent.block_size

    def blocks_length(self):
        number_of_blocks = self.piece_length / Torrent.block_size
        b_left_overs = number_of_blocks % 1
        b_rest = b_left_overs * Torrent.block_size
        if b_rest == 0:
            return Torrent.block_size
        else:
            return b_rest
        
    def num_block_of_last_piece(self):
        return self.last_piece_length() / Torrent.block_size

    def last_block_of_last_piece(self):
        num_block_of_last_piece = self.last_piece_length() / Torrent.block_size
        l_b_left_overs = num_block_of_last_piece % 1
        l_b_rest = l_b_left_overs * Torrent.block_size
        if l_b_rest == 0:
            return Torrent.block_size
        else:
            return l_b_rest
        
class Message():

    def encode(self):
        raise NotImplementedError

    def decode(self):
        raise NotImplementedError

class KeepAlive(Message):

    def __init__(self):
        pass
    def encode(self):
        return struct.pack('!I', 0)
    def decode(self):
        return struct.unpack()

class Choke(Message):
    ID = 0
    def encode(self):
        return struct.pack('!Ib', 1, Choke.ID)

    @classmethod
    def decode(cls, data):
        return struct.unpack('!Ib', 1, cls.ID)
    
    def __str__(self):
        return 'Choke'

class Unchoke(Message):
    ID = 1
    def encode(self):
        return struct.pack('!Ib', 1, Unchoke.ID)

    @classmethod
    def decode(cls, data):
        return struct.unpack('!Ib', 1, cls.ID)
    
    def __str__(self):
        return 'Unchoke'

class Interested(Message):
    ID = 2
    def encode(self):
        return struct.pack('!Ib', 1, Interested.ID)

    @classmethod
    def decode(cls, data):
        return struct.unpack('!Ib', 1, cls.ID)
    
    def __str__(self):
        return 'Interested'

class Not_Interested(Message):
    ID = 3
    def encode(self):
        return struct.pack('!Ib', 1, Not_Interested.ID)

    @classmethod
    def decode(cls, data):
        message_id = cls.ID
        return struct.unpack('!Ib', 1, cls.ID)
    
    def __str__(self):
        return 'Not Interested'

class Have(Message):
    ID = 4
    def __init__ (self, piece_index):
        self.piece_index = piece_index
    
    def encode(self):
        pass
    def decode(self):
        pass


class Bitfield(Message):
    ID = 5
    def __init__ (self, bitfield):
        self.bitfield = bitfield

    def encode(self):
        pass

    @classmethod
    def decode(cls, bitfield_message):
        processed_message_metadata = struct.unpack('!Ib', bitfield_message[0:5])
        # Remove 1, left out message ID
        bitfield_len = processed_message_metadata[0] - 1
        bitfield_array = bitstring.BitArray(bitfield_message[6:bitfield_len])
        assert len(bitfield_array.bin) % 8 == 0
        return Bitfield(bitfield_array)

class Request(Message):
    ID = 6
    def __init__(self, index, begin, length):
        self.index = index
        self.begin = begin
        self.length = length

    def encode(self):
        format_string = f'!IbIII'
        return struct.pack(format_string, 13, Request.ID, self.index, self.begin, self.length)

    def decode(self):
        raise NotImplementedError('Peer Request decode message not implemented')

class Piece(Message):
    ID = 7
    LEN_WITHOUT_BLOCK_DATA = 9

    def __init__ (self, index, begin, block):
        self.index = index
        self.begin = begin
        self.block = block

    def encode(self):
        pass

    @classmethod
    def decode(cls, piece_message):
        length = struct.unpack('>I', piece_message[:4])[0]
        parts = struct.unpack('>IbII' + str(length - Piece.LEN_WITHOUT_BLOCK_DATA) + 's',
                              piece_message[:length+4])
        return cls(parts[2], parts[3], parts[4])
    
    def __str__(self) -> str:
        return f'index: {self.index} begin: {self.begin} block: {self.block}'

class Cancel(Message):
    ID = 8
    
    def encode(self):
        raise NotImplementedError('Peer Cancel encode message not implemented')
    def decode(self):
        raise NotImplementedError('Peer Cancel decode message not implemented')

class Port(Message):
    ID = 9
    
    def encode(self):
        raise NotImplementedError('Peer Port encode message not implemented')
    def decode(self):
        raise NotImplementedError('Peer Port decode message not implemented')

ID_to_msg_class = {
                   None:KeepAlive,
                      0:Choke,
                      1:Unchoke,
                      2:Interested,
                      3:Not_Interested,
                      4:Have,
                      5:Bitfield,
                      6:Request,
                      7:Piece,
                      8:Cancel,
                      9:Port
                  }
