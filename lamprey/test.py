from math import ceil


file = 1151975424
piece_length = 262144
total_number_of_piece = ceil(file/ piece_length)
block_size = 2**14
ilosc_blokow = ceil(piece_length / block_size)
blocks_in_file = file / block_size                      #70311
#number_of_piece * (ilosc_blokow * block_size)

def file_begin(block_size, piece_index, block_index):
    if piece_index == 0:
        total_block_index = block_index
    if piece_index == 1 and block_index == 0:
        total_block_index = piece_index * ilosc_blokow
        begin = total_block_index  * block_size
    else:
        total_block_index = piece_index * ilosc_blokow
        begin = (total_block_index + block_index)  * block_size
    end = begin + block_size - 1
    return begin


    #TODO Tym sie zająć żeby działał begin i end w piece_manager    , total block index musi wskazywać faktyczny stan block indexu


    # total_block_index dla piecu 0 bloku 0 = 0 , powinien byc 0
    # total_block_index dla piecu 0 bloku 1 = 0 , powinien być 1
    # total_block_index dla piecu 0 bloku 2 = 0 , powinien być 2
    # total_block_index dla piecu 0 bloku 3 = 0 , powineien być 3
    # ...
    # total_block_index dla piecu 0 bloku 15 = 0 , powinien być 15
    # total_block_index dla piecu 1 bloku 0 = 16 , powinien być 16
    # ...
    # total_block_index dla piecu 2 bloku 0 = 32 , powinien być 32
    
    
    
    
    
    
    
    # blocks_number = number_of_piece * number_of_block
    # return (blocks_number +)
    # number_of_piece * number_of_block
    # blok =  numer bloku 
    # wynik = Piece + Blok * block_size

    # zero_block = 0 + 262143
    # # return 0
    # x = 262143
    # wielkość_bloku_w_piece = 

    # zero_block = 0 + 16383
    # pierwszy_block = 16384 + 16383 ==  32767
    # drugi_block = 32768 + 16383 == 49151
    # trzeci_block = 49152 + 16383 == 65534
    # ....
    # pietnasty_block = 245760 + 16383 == 262143

def file_begin_test():
    assert file_begin(block_size, piece_index = 0, block_index=0) == 0
    assert file_begin(block_size, piece_index= 0, block_index=1) == 16384
    assert file_begin(block_size, piece_index= 0, block_index=2) == 32768
    assert file_begin(block_size, piece_index= 0, block_index=3) == 49152
    assert file_begin(block_size, piece_index= 0, block_index=15) == 245760
    print(file_begin(block_size, piece_index= 1, block_index=0))
    assert file_begin(block_size, piece_index= 1, block_index=0) == 262144
    assert file_begin(block_size, piece_index= 1, block_index=7) == 376832
    print(file_begin(block_size, piece_index= 5, block_index=7))
    assert file_begin(block_size, piece_index= 5, block_index=7) == 1425408
    assert file_begin(block_size, piece_index= 4394, block_index=6) == 1151959040
    assert file_begin(block_size, piece_index= 4394, block_index=7) == 1151975424

file_begin_test()

# piece_index = int(input()) * number_of_block
# block_index = int(input())
# begin = (piece_index + block_index) * block_size
# end = begin + block_size - 1
# # print(begin)
# # print(end)