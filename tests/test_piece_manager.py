import pytest
from unittest.mock import patch

from lamprey.tracker import Tracker
from lamprey.dataclass import Torrent
from lamprey.piece_manager import FileManager
from datetime import datetime
import bencoding

TEST_CASES = [
    {
        'torrent_file': 'tests/torrent-files/debian-live-11.5.0-amd64-standard.iso.torrent',
        'expected_first_piece_first_block_begin': 0,
        'expected_first_piece_last_block_end': 262143,
        'expected_second_piece_first_block_begin': 262144,
        'expected_second_piece_last_block_end': 524287,
        'expected_last_piece_last_block_begin': 1151959040,
        'expected_last_piece_last_block_end': 1151975424,
        'expected_last_piece_last_block_size': 16384,
    },
]


@pytest.fixture(scope='module', params=TEST_CASES)
def torrent_info(request):
    test_case = request.param
    with open(test_case['torrent_file'], 'rb') as fp:
        FILE = fp.read()
    torrent_file = bencoding.bdecode(FILE)
    
    torrent = Torrent((torrent_file[b"comment"]), (torrent_file[b"created by"]), (datetime.fromtimestamp(torrent_file[b"creation date"])),  (
    torrent_file[b"url-list"]), (torrent_file[b"info"]), (torrent_file[b'info'][b'name']), (torrent_file[b'info'][b'length']), (torrent_file[b'info'][b'piece length']), (torrent_file[b'announce']), (torrent_file[b'announce-list']))

    return {
        'bitfield': FileManager(torrent).bitfield,
        'expected_values': {
            'first_piece_first_block_begin': test_case['expected_first_piece_first_block_begin'],
            'first_piece_last_block_end': test_case['expected_first_piece_last_block_end'],
            'second_piece_first_block_begin': test_case['expected_second_piece_first_block_begin'],
            'second_piece_last_block_end': test_case['expected_second_piece_last_block_end'],
            'last_piece_last_block_begin': test_case['expected_last_piece_last_block_begin'],
            'last_piece_last_block_end': test_case['expected_last_piece_last_block_end'],
            'last_piece_last_block_size': test_case['expected_last_piece_last_block_size'],
        }
    }

def test_bitfield_first_piece_first_block_begin(torrent_info):
    expected = torrent_info['expected_values']['first_piece_first_block_begin']
    actual = torrent_info['bitfield'][0].block_list[0].begin
    assert expected == actual

def test_bitfield_first_piece_last_block_end(torrent_info):
    expected = torrent_info['expected_values']['first_piece_last_block_end']
    actual = torrent_info['bitfield'][0].block_list[-1].end
    assert expected == actual

def test_bitfield_second_piece_first_block_begin(torrent_info):
    expected = torrent_info['expected_values']['second_piece_first_block_begin']
    actual = torrent_info['bitfield'][1].block_list[0].begin
    assert expected == actual

def test_bitfield_second_piece_last_block_end(torrent_info):
    expected = torrent_info['expected_values']['second_piece_last_block_end']
    actual = torrent_info['bitfield'][1].block_list[-1].end
    assert expected == actual

def test_bitfield_last_piece_last_block_begin(torrent_info):
    expected = torrent_info['expected_values']['last_piece_last_block_begin']
    actual = torrent_info['bitfield'][-1].block_list[-1].begin
    assert expected == actual

def test_bitfield_last_piece_last_block_end(torrent_info):
    expected = torrent_info['expected_values']['last_piece_last_block_end']
    actual = torrent_info['bitfield'][-1].block_list[-1].end
    print(actual)
    assert expected == actual

def test_bitfield_last_piece_last_block_size(torrent_info):
    expected = torrent_info['expected_values']['last_piece_last_block_size']
    actual = torrent_info['bitfield'][-1].block_list[-1].size
    assert expected == actual





# import pytest
# from unittest.mock import patch
# from lamprey.tracker import Tracker
# from lamprey.dataclass import Torrent
# from lamprey.piece_manager import FileManager
# from datetime import datetime
# import bencoding

# # Define test cases with input torrent file paths and expected values
# TEST_CASES = [
#     {
#         'torrent_file': 'tests/torrent-files/debian-live-11.5.0-amd64-standard.iso.torrent',
#         'expected_first_piece_first_block_begin': 0,
#         'expected_first_piece_last_block_end': 262143,
#         'expected_second_piece_first_block_begin': 262144,
#         'expected_second_piece_last_block_end': 524287,
#         'expected_last_piece_last_block_begin': 1151959040,
#         'expected_last_piece_last_block_end': 1151975424,
#         'expected_last_piece_last_block_size': 16384,
#     },
#     # Add more test cases as needed
# ]

# @pytest.fixture(scope='module', params=TEST_CASES)
# def torrent_info(request):
#     test_case = request.param
#     with open(test_case['torrent_file'], 'rb') as fp:
#         FILE = fp.read()
#     torrent = bencoding.bdecode(FILE)

#     return {
#         'comment': torrent[b"comment"],
#         'created_by': torrent[b"created by"],
#         'creation_date': datetime.fromtimestamp(torrent[b"creation date"]),
#         'url_list': torrent[b"url-list"],
#         'info': torrent[b"info"],
#         'name': torrent[b'info'][b'name'],
#         'length': torrent[b'info'][b'length'],
#         'piece_length': torrent[b'info'][b'piece length'],
#         'announce': torrent[b'announce'],
#         'announce_list': torrent[b'announce-list'],
#         'expected_values': {
#             'first_piece_first_block_begin': test_case['expected_first_piece_first_block_begin'],
#             'first_piece_last_block_end': test_case['expected_first_piece_last_block_end'],
#             'second_piece_first_block_begin': test_case['expected_second_piece_first_block_begin'],
#             'second_piece_last_block_end': test_case['expected_second_piece_last_block_end'],
#             'last_piece_last_block_begin': test_case['expected_last_piece_last_block_begin'],
#             'last_piece_last_block_end': test_case['expected_last_piece_last_block_end'],
#             'last_piece_last_block_size': test_case['expected_last_piece_last_block_size'],
#         }
#     }

# def test_debian_bitfield_first_piece_first_block_begin(torrent_info):
#     expected = torrent_info['expected_values']['first_piece_first_block_begin']
#     actual = torrent_info['bitfield'][0].block_list[0].begin
#     assert expected == actual

# # Define similar test functions for other expected values

# # Run tests with different test cases
