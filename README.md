# TOR-Networking

A hands-on exploration of anonymizing network traffic through Tor, in
three progressively more advanced modes - from simply routing through Tor,
to customizing which countries your traffic enters/exits through, to
genuinely rotating circuits on demand using Tor's own control protocol.

## Modes

| Mode | File | What it does |
|---|---|---|
| **Basic** | `create_basic_tor_proxy.py` | Launches a local Tor process and routes a request through it via the SOCKS proxy |
| **Intermediate** | `create_intermediate_tor_proxy.py` | Same as Basic, but pins the entry/exit relay countries (France entry, Spain exit in the current config) using Tor's GeoIP data |
| **Advanced** | `create_advanced_tor_proxy.py` | Launches Tor with control-port access, then genuinely rotates to a fresh circuit multiple times using the `NEWNYM` signal, printing the new relay path and exit IP after each rotation |

Supporting scripts:
- `check_ip.py` - shared utility: checks the current exit IP/country through the Tor SOCKS proxy (used by all three modes above)
- `check_tor_network.py` - inspects and prints the currently active Tor circuit without launching a new Tor process (useful if Tor's already running)
- `setup_tor.py` - one-time setup script that fetches Tor itself (see Setup below)

## Tech stack

- Python 3.x
- [`stem`](https://stem.torproject.org/) - Python controller library for Tor, used to launch Tor, authenticate to its control port, and send control signals like `NEWNYM`
- `requests` - SOCKS-proxied HTTP requests
- Tor itself - fetched on demand by `setup_tor.py` directly from the official Tor Project (**not committed to this repo** - see Setup below for why)

## Setup

**This project is currently Windows-only** (paths are hardcoded with Windows-style separators).

1. Install Python dependencies:
   ```bash
   pip install stem requests
   ```
2. Run the setup script to fetch Tor automatically:
   ```bash
   python setup_tor.py
   ```
   This downloads the current official Tor Expert Bundle directly from
   torproject.org and extracts it to `tor/tor.exe`. Fetching it this way
   (rather than committing the binary to the repo) means you always get
   an official, current, verifiable copy straight from the source - if
   the automatic download ever fails, the script prints a link to the
   official download page so you can grab it manually instead.

## Running each mode

```bash
python create_basic_tor_proxy.py          # simple Tor-routed request
python create_intermediate_tor_proxy.py   # France entry / Spain exit
python create_advanced_tor_proxy.py       # 5 rotations of a fresh circuit each time
```

`create_advanced_tor_proxy.py` will print the circuit path and exit IP once initially, then again after each of 5 circuit rotations - you should see the exit IP and relay fingerprints genuinely change between rotations.

To just inspect an already-running Tor circuit without launching a new process:
```bash
python check_tor_network.py
```

## What I learned / what I'd improve

Tor anonymizes **who** is connecting - the destination server only ever sees the exit relay's IP, never yours. It does **not** encrypt the **content** of already-unencrypted traffic: these scripts check IP over plain HTTP (`http://ip-api.com`), which means the exit relay itself can see that request's contents in plaintext as it leaves the Tor network. This is a commonly confused distinction worth being precise about: Tor protects origin/identity, not confidentiality of unencrypted payloads. Using HTTPS destinations keeps the payload encrypted end-to-end, even from the exit relay.

Things I'd improve with more time:
- Add HTTPS-based IP checking as an option, to demonstrate the origin-anonymity-vs-content-encryption distinction concretely (e.g., show identical Tor anonymity with and without payload encryption)
- Cross-platform support (currently Windows-only due to hardcoded paths)
- Configurable rotation count/interval via command-line arguments instead of constants in the file

## Known limitations

- Windows-only currently (hardcoded `tor.exe` path with backslashes)
- The Intermediate mode's country selection (`EntryNodes: '{FR}'`, `ExitNodes: '{ES}'`) is hardcoded in the script rather than configurable at runtime
- `setup_tor.py` relies on scraping the official Tor download page for the current bundle link — if Tor Project ever restructures that page, the script falls back to printing manual download instructions rather than failing silently

## Full write-up

The reasoning behind each mode, and the Tor-anonymity-vs-encryption distinction in more depth: https://quietbytes.hashnode.dev/tor-proxy-python-circuit-rotation
