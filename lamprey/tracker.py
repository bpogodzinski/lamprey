from lamprey.dataclass import Torrent
import requests
from hashlib import sha1
from random import randint
import bencoding
import urllib.parse
import logging


class Tracker:
    """
    Class representing a tracker for a given torrent
    """
    # static variables
    client_identifier = '-LR2137-'
    info_hash = None

    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        # default port for BitTorrent connections
        self.port = 6889
        self.peer_id = self._generate_peer_id()
        if not Tracker.info_hash:
            Tracker.info_hash = self._generate_info_hash

    def _generate_info_hash(self, torrent: Torrent) -> str:
        """Generate sha1 hash of *info* torrent dict value

        Args:
            info_dict (dict): Metafile 'info' key value

        Returns:
            str: Hash of info key
        """
        return sha1(bencoding.bencode(torrent.get_info())).digest()

    def _generate_peer_id(self) -> str:
        """Generate peer_id

        Returns:
            str: ID that follows convention <client_identifier><12 random digits>
        """
        return f"{Tracker.client_identifier}{''.join([str(randint(0,9)) for _ in range(12)])}"

    def connect(self, first: bool = False, uploaded: int = 0,
                downloaded: int = 0) -> requests.Response:
        """Connect to the tracker and return response

        Args:
            first (bool, optional): Is it the first time connect to tracker?. Defaults to False.
            uploaded (int, optional): Bytes already uploaded to peers. Defaults to 0.
            downloaded (int, optional): Bytes already downloaded to peers. Defaults to 0.

        Raises:
            ConnectionError: raised if 400 or 500
            NotImplementedError: WIP

        Returns:
            requests.Response: response from tracker server
        """

        url = self._create_announce_url()
        # FIXME: getting 404
        # TODO: Learn http codes, difference between GET and POST
        response = requests.get(url)
        print(response)

    def _create_announce_url(self) -> str:
        """Create encoded url to get peer information

        Raises:
            NotImplementedError: WIP

        Returns:
            str: URL to connect to. Ex:
            http://torrent.ubuntu.com:6969/announce?
            info_hash=%90%28%9F%D3M%FC%1C%F8%F3%16%A2h%AD%D85L%853DX&
            peer_id=-LR2137-706887310628&
            uploaded=0&
            downloaded=0&
            left=699400192&
            port=6889&
            compact=1
        """
        info_hash = self._generate_info_hash(self.torrent)
        info_hash_encoded = urllib.parse.quote(info_hash)
        for announce_url in self.torrent.get_url_list():
            tracker_url = announce_url.decode()
            url = f"{tracker_url}announce?info_hash={info_hash_encoded}&peer_id={self._generate_peer_id()}&uploaded={0}&downloaded={0}&port={self.port}&left={self.torrent.get_length()}&compact={1}"
            response = requests.get(url)
            if response.status_code == 200:
                logging.info(tracker_url)
