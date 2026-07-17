import requests
import json
from datetime import datetime

PROXIES = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}


def check_current_ip(proxies=None):
    """
    Queries ip-api.com through the given proxies (defaults to the local Tor
    SOCKS proxy on port 9050) and prints/returns the current exit IP and
    country.

    NOTE: this request is made over plain HTTP, not HTTPS. Tor anonymizes
    *who* is connecting -- ip-api.com only ever sees the Tor exit relay's
    IP, never yours. But Tor does not encrypt the *content* of an
    already-unencrypted HTTP request: the exit relay itself can see this
    traffic's contents in plaintext as it exits the Tor network. This is a
    commonly confused distinction -- Tor protects your identity/origin, not
    the confidentiality of unencrypted traffic. Using HTTPS destinations
    keeps the payload encrypted end-to-end even from the exit relay.
    """
    proxies = proxies or PROXIES
    response = requests.get("http://ip-api.com/json/", proxies=proxies)
    result = json.loads(response.content)
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print('TOR IP [%s]: %s %s' % (timestamp, result["query"], result["country"]))
    return result


if __name__ == "__main__":
    check_current_ip()
