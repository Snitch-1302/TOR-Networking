from stem.control import Controller
from stem import CircStatus

from check_ip import check_current_ip


def print_current_circuit(controller):
    """Prints the relays (entry -> middle -> exit) in the currently active circuit."""
    for circ in sorted(controller.get_circuits()):
        print(circ.status)
        if circ.status == CircStatus.BUILT:
            print("Circuit %s (%s)" % (circ.id, circ.purpose))
            for i, entry in enumerate(circ.path):
                div = '+' if (i == len(circ.path) - 1) else '|'
                fingerprint, nickname = entry
                desc = controller.get_network_status(fingerprint, None)
                address = desc.address if desc else 'unknown'
                print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))


if __name__ == "__main__":
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        print_current_circuit(controller)
        check_current_ip()
