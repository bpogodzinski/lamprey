#!/bin/bash

if ! [[ -d "venv" ]]
then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source venv/bin/activate
python -m lamprey -vv tests/torrent-files/archlinux-2022.10.01-x86_64.torrent 