#!/bin/bash

if ! [[ -d "venv" ]]
then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source venv/bin/activate
python -m lamprey -vv tests/torrent-files/debian-live-11.5.0-amd64-standard.iso.torrent