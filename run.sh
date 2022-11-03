#!/bin/bash

if ! [[ -d "venv" ]]
then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

source venv/bin/activate
python -m lamprey -h tests -h torrent-file SXSW_2020_Showcasing_Artists_Part2.torrent