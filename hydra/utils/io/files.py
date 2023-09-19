import hashlib
import json
import os


def read_json(file, path=None):
    if path:
        file = os.path.join(path, file)
    with open(file) as f:
        return json.load(f)


def generate_file_hash(file_content: bytes) -> str:
    readable_hash = hashlib.sha256(file_content).hexdigest()
    return readable_hash
