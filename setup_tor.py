"""
setup_tor.py

Downloads the current Tor Expert Bundle for Windows directly from the
official Tor Project, and extracts tor.exe (plus its supporting files)
into tor/, so the other scripts in this repo can find it at tor/tor.exe.

Run this once before using create_basic_tor_proxy.py,
create_intermediate_tor_proxy.py, or create_advanced_tor_proxy.py.
"""

import os
import re
import shutil
import tarfile
import tempfile
import requests

DOWNLOAD_PAGE = "https://www.torproject.org/download/tor/"
TARGET_DIR = os.path.join(os.getcwd(), "tor")


def find_latest_bundle_url():
    """
    Scrapes the official Tor download page for the current Windows x86_64
    Expert Bundle link, rather than hardcoding a version number that would
    go stale the moment Tor ships an update. Returns None if the page
    structure has changed and the pattern can't be found -- the caller
    falls back to manual instructions in that case.
    """
    response = requests.get(DOWNLOAD_PAGE, timeout=15)
    response.raise_for_status()

    match = re.search(
        r'https://dist\.torproject\.org/torbrowser/[\d.a-z]+/'
        r'tor-expert-bundle-windows-x86_64-[\d.a-z]+\.tar\.gz',
        response.text,
    )
    return match.group(0) if match else None


def download_and_extract(bundle_url):
    print(f"[+] Downloading Tor Expert Bundle from:\n    {bundle_url}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = os.path.join(tmp_dir, "tor-expert-bundle.tar.gz")

        response = requests.get(bundle_url, stream=True, timeout=60)
        response.raise_for_status()
        with open(archive_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("[+] Extracting archive...")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(tmp_dir)

        # The expert bundle extracts to a "tor/" folder containing tor.exe
        # and its dependencies (DLLs, etc.) -- copy that whole folder in.
        extracted_tor_dir = os.path.join(tmp_dir, "tor")
        if not os.path.isdir(extracted_tor_dir):
            raise RuntimeError(
                "Expected an extracted 'tor/' folder inside the archive but "
                "didn't find one -- the bundle's internal layout may have "
                "changed. Check the archive manually."
            )

        if os.path.isdir(TARGET_DIR):
            shutil.rmtree(TARGET_DIR)
        shutil.copytree(extracted_tor_dir, TARGET_DIR)

    print(f"[+] Done. Tor installed at: {os.path.join(TARGET_DIR, 'tor.exe')}")


def main():
    existing = os.path.join(TARGET_DIR, "tor.exe")
    if os.path.isfile(existing):
        print(f"[i] tor.exe already exists at {existing} -- nothing to do.")
        print("    Delete the tor/ folder first if you want to force a re-download.")
        return

    print("[+] Looking up the current Tor Expert Bundle download link...")
    bundle_url = find_latest_bundle_url()

    if not bundle_url:
        print(
            "[!] Could not automatically find the download link.\n"
            f"    Please download it manually from {DOWNLOAD_PAGE}\n"
            "    (choose the Windows Expert Bundle), then extract it so that\n"
            "    tor.exe ends up at tor/tor.exe in this project's root."
        )
        return

    download_and_extract(bundle_url)


if __name__ == "__main__":
    main()
