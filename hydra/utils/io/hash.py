import hashlib
from pickle import dumps


def generate_hash_from_obj(obj: object) -> str:
    return generate_hash_from_bytes(dumps(obj))

def generate_hash_from_bytes(content: bytes) -> str:
    readable_hash = hashlib.sha256(content).hexdigest()
    return readable_hash