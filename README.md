# Lamprey - Simple CLI BitTorrent client written in Python <!-- omit in toc -->

**lamprey** *noun*

1. Any eellike marine or freshwater fish of the order *Petromyzoniformes*, having a circular, suctorial mouth with horny teeth for boring into the flesh of other fishes to feed on their blood.

# Table of Contents <!-- omit in toc -->

- [Installing and running](#installing-and-running)
- [Goals](#goals)
- [Backlog](#backlog)

## Installing and running

```text
git clone ssh://git@github.com/Lamprey-BitTorrent/lamprey-cli.git
cd lamprey-cli
python3 -m lamprey-cli -v archlinux-2022.05.01-x86_64.iso.torrent
```

## Goals

v1.0

- [ ] Parse magnetlinks
- [ ] Connect to trackers
- [ ] Figure out sequence of download
  - [ ] Download sequentially
- [ ] Progress bar
- [ ] Renew progress after interruption or cancel
- [ ] Proxy
- [ ] Figure out upload

## Backlog

- [ ] Prepare wiki/pages as a documentation about `Lamprey` and BitTorrent technology
- [ ] Prepare milestones, issues and divide the tasks
