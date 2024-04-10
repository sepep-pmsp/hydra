import json
import os


from .hash import generate_hash_from_bytes

def read_json(file, path=None):
    if path:
        file = os.path.join(path, file)
    with open(file) as f:
        return json.load(f)


def generate_file_hash(file_content: bytes) -> str:
    return generate_hash_from_bytes(file_content)
