from dataclasses import dataclass

@dataclass
class Torrent:
    """Class for keeping torrent data"""
    data_1: None
    data_2: None
    name: None

    def get_name(self) -> str:
        return self.name
    
    def get_data_1(self) -> float:
        return self.data_1