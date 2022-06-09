import hashlib
import requests
from random import randint

class Tracker:
    """
    Class representing a tracker for a given torrent
    """
    # check if user have space!
    # static variables
    client_identifier = '-LR2137-'
    # TODO: move to torrent class
    info_hash = None


    def __init__(self, torrent) -> None:
        self.torrent = torrent
        # default port for BitTorrent connections
        self.port = 6889
        self.peer_id = self._generate_peer_id()
        if not Tracker.info_hash:
            Tracker.info_hash = self._generate_info_hash(self.info_dict)

    def _generate_info_hash(self, info_dict: dict) -> str:
        """Generate sha1 hash of *info* torrent dict value"""
        raise NotImplementedError
    
    def _generate_peer_id(self) -> str:
        """Generate peer_id
        peer_id follow convention:
        <client_identifier><12 random digits>"""
        raise NotImplementedError

    def connect(self, first: bool = False, uploaded: int = 0,
                downloaded: int = 0) -> requests.Response:
        """Connect to the tracker and return
        response"""
        raise NotImplementedError

    def _create_announce_url(self) -> str:
        """Create encoded url to get peer information"""
        raise NotImplementedError

    