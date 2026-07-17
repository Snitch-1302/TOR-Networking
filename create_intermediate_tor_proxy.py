import os
import re
import urllib.request
import stem.process

from check_ip import check_current_ip

SOCKS_PORT = 9050
CONTROL_PORT = 9051
TOR_PATH = os.path.normpath(os.getcwd() + "\\tor\\tor.exe")
GEOIPFILE_PATH = os.path.normpath(os.getcwd() + "\\data\\tor\\geoip")

try:
    urllib.request.urlretrieve(
        'https://raw.githubusercontent.com/torproject/tor/main/src/config/geoip',
        GEOIPFILE_PATH
    )
except Exception:
    print('[INFO] Unable to update geoip file. Using local copy.')

tor_process = stem.process.launch_tor_with_config(
    config={
        'SocksPort': str(SOCKS_PORT),
        'ControlPort': str(CONTROL_PORT),
        'EntryNodes': '{FR}',
        'ExitNodes': '{ES}',
        'StrictNodes': '1',
        'CookieAuthentication': '1',
        'MaxCircuitDirtiness': '60',
        'GeoIPFile': GEOIPFILE_PATH,
    },
    init_msg_handler=lambda line: print(line) if re.search('Bootstrapped', line) else False,
    tor_cmd=TOR_PATH
)

check_current_ip()

tor_process.kill()
