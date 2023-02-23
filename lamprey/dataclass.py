import struct
import logging

class Torrent():
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


'''
wszystko za i de kodowywujemy za pomocą struct
# format-characters do formatowania wiadomości
https://docs.python.org/3/library/struct.html

handshake_format = '!B19s8x20s20s'
message = struct.pack(handshake_format, 19, 'BitTorrent protocol'.encode('utf-8'),
                      tracker.info_hash, tracker.peer_id.encode('utf-8'))

peer_response = struct.unpack(handshake_format, data)


message nadrzędna, abstrakcyjna
<length prefix><message ID><payload>
puste metody, abstrakcyjne
- zakodowujemy (bajty)
- dekodujemy (liste/tuple)

klasy dziedziczące z message
keep-alive: <len=0000>
- zakodować
- dekodować
choke: <len=0001><id=0>
- zakodować
- dekodować
unchoke: <len=0001><id=1>
- zakodować
- dekodować
interested: <len=0001><id=2>
- zakodować
- dekodować
not interested: <len=0001><id=3>
- zakodować
- dekodować
have: <len=0005><id=4><piece index>
- zakodować
- dekodować
bitfield: <len=0001+X><id=5><bitfield>
- zakodować
- dekodować
request: <len=0013><id=6><index><begin><length>
- zakodować
- dekodować
piece: <len=0009+X><id=7><index><begin><block>
- zakodować
- dekodować
cancel: <len=0013><id=8><index><begin><length>
- zakodować
- dekodować
port: <len=0003><id=9><listen-port>
- zakodować
- dekodować

'''

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
    def decode(self):
        pass

class Request(Message):
    ID = 6
    def __init__(self, index, begin, length):
        self.index = index
        self.begin = begin
        self.length = length

    def encode(self):
        format_string = f'!B'
        # return struct.pack(format_string, self.length)

    def decode(self):
        raise NotImplementedError('Peer Request decode message not implemented')

class Piece(Message):
    ID = 7
    def __init__ (self, index, begin, block):
        self.index = index
        self.begin = begin
        self.block = block

    def encode(self):
        pass
    def decode(self):
        pass

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
                     -1:KeepAlive,
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
