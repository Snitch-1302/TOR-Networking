import os
import re
import time
import stem.process
from stem.control import Controller
from stem import Signal, CircStatus

from check_ip import check_current_ip

SOCKS_PORT = 9050
CONTROL_PORT = 9051
TOR_PATH = os.path.normpath(os.getcwd() + "\\tor\\tor.exe")

# How many times to rotate to a fresh circuit, and how long to wait between
# rotations. Tor enforces its own internal rate limit on NEWNYM (roughly
# once every 10 seconds) -- requesting it faster than that is silently
# ignored, so this waits comfortably longer than that minimum.
NUM_ROTATIONS = 5
SECONDS_BETWEEN_ROTATIONS = 15
SECONDS_TO_LET_CIRCUIT_BUILD = 5


def print_current_circuit(controller):
    """Prints the relays (entry -> middle -> exit) in the currently active circuit."""
    for circ in sorted(controller.get_circuits()):
        if circ.status == CircStatus.BUILT:
            print("Circuit %s (%s)" % (circ.id, circ.purpose))
            for i, entry in enumerate(circ.path):
                div = '+' if (i == len(circ.path) - 1) else '|'
                fingerprint, nickname = entry
                desc = controller.get_network_status(fingerprint, None)
                address = desc.address if desc else 'unknown'
                print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))


def rotate_circuit(controller):
    """
    Requests a brand new circuit via Tor's NEWNYM signal. This is the actual
    mechanism behind "dynamic circuit formation" -- it tells Tor to abandon
    its current circuit and build a fresh one (new entry/middle/exit relays)
    for any new connections, rather than reusing the same path.
    """
    controller.signal(Signal.NEWNYM)
    time.sleep(SECONDS_TO_LET_CIRCUIT_BUILD)  # give Tor time to actually build the new path


def main():
    tor_process = stem.process.launch_tor_with_config(
        config={
            'SocksPort': str(SOCKS_PORT),
            'ControlPort': str(CONTROL_PORT),
            'CookieAuthentication': '1',
        },
        init_msg_handler=lambda line: print(line) if re.search('Bootstrapped', line) else False,
        tor_cmd=TOR_PATH
    )

    try:
        with Controller.from_port(port=CONTROL_PORT) as controller:
            controller.authenticate()

            print("--- Initial circuit ---")
            print_current_circuit(controller)
            check_current_ip()

            for rotation in range(1, NUM_ROTATIONS + 1):
                print(f"\n--- Rotation {rotation}/{NUM_ROTATIONS} ---")
                rotate_circuit(controller)
                print_current_circuit(controller)
                check_current_ip()

                if rotation < NUM_ROTATIONS:
                    time.sleep(SECONDS_BETWEEN_ROTATIONS)
    finally:
        tor_process.kill()


if __name__ == "__main__":
    main()
