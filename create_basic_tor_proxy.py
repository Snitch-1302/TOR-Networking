import os
import re
import stem.process

from check_ip import check_current_ip

SOCKS_PORT = 9050
TOR_PATH = os.path.normpath(os.getcwd() + "\\tor\\tor.exe")

tor_process = stem.process.launch_tor_with_config(
    config={
        'SocksPort': str(SOCKS_PORT),
    },
    init_msg_handler=lambda line: print(line) if re.search('Bootstrapped', line) else False,
    tor_cmd=TOR_PATH
)

check_current_ip()

tor_process.kill()
