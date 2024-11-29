import hashlib
import json
import os
from datetime import datetime


def calculate_sha256(file_path):
    # Open the file in binary mode
    with open(file_path, "rb") as f:
        # Create a SHA256 hash object
        sha256_hash = hashlib.sha256()
        # Read the file in chunks and update the hash object
        while True:
            data = f.read(4096)  # Read 4KB at a time
            if not data:
                break
            sha256_hash.update(data)
    # Get the hexadecimal representation of the hash
    file_hash = sha256_hash.hexdigest()
    return file_hash


# Calculates the checksums of all files in a given list
def calculate_checksums(files: list[str]) -> dict:
    checksum_entry = {"timestamp": str(datetime.now()), "checksums": {}}
    for file in files:
        checksum_entry["checksums"][file] = calculate_sha256(file)
    return checksum_entry


# Get the checksums from a previous run on the specified target and inventory
def read_checksums(checksum_file: str, host: str, inventory: str) -> dict:
    if not os.path.isfile(checksum_file):
        path, _ = os.path.split(checksum_file)
        os.makedirs(path, exist_ok=True)
        return None
    if os.stat(checksum_file).st_size == 0:
        return None
    with open(checksum_file, "r") as f:
        checksums = json.load(f)
        if host in checksums and inventory in checksums[host]:
            return checksums[host][inventory]
        return None


# Writes the checksums to the target file
def write_checksums(
    checksum_file: str, host: str, inventory: str, checksum_patch: dict
):
    if os.path.isfile(checksum_file) and os.stat(checksum_file).st_size != 0:
        with open(checksum_file, "r") as f:
            checksums = json.load(f)
        if not host in checksums:
            checksums[host] = {}
        checksums[host][inventory] = checksum_patch
        with open(checksum_file, "w") as f:
            json.dump(checksums, f, indent=2)
    else:
        checksums = {}
        checksums[host] = {}
        checksums[host][inventory] = checksum_patch
        with open(checksum_file, "w") as f:
            json.dump(checksums, f, indent=2)


# Returns true if the checksums in previous and current are the same and else false
def are_checksums_equal(previous: dict, current: dict) -> bool:
    if len(previous) != len(current):
        return False
    for file_name, hash in previous.items():
        if file_name in current and current[file_name] == hash:
            continue
        else:
            return False
    return True
