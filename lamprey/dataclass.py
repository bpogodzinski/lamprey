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
