import pytest
from unittest.mock import patch
import bencoder

from lamprey.tracker import Tracker

def bin_to_str(dictionary):
    str_dict = {}
    for k, v in dictionary.items():
        key = k.decode('latin-1')
        try:
            str_dict[key] = v.decode('latin-1')
        except AttributeError:
            str_dict[key] = v
    return str_dict

@pytest.fixture(scope='module')
def torrent_file():
    torrent_dict = {}
    FILEPATH = 'archlinux-2022.05.01-x86_64.iso.torrent'
    with open(FILEPATH, 'rb') as fp:
        return bencoder.decode(fp.read())

@patch('lamprey.tracker.randint', autospec=True, return_value=7)
def test_generate_peer_id(mock_randint):
    tracker = Tracker(torrent_file)
    expected = f"{Tracker.client_identifier}{''.join(['7' for _ in range(12)])}"
    actual = tracker.generate_peer_id()
    assert len(actual) == 20
    assert expected == actual

def test_generate_info_hash(torrent_file):
    tracker = Tracker(torrent_file)
    info_dict = torrent_file[b'info']
    actual = tracker.generate_info_hash(info_dict)
    expected = '9B4C1489BFCCD8205D152345F7A8AAD52D9A1F57'
    assert expected == actual