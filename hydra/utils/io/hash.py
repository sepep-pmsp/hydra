import hashlib
from pickle import dumps


def generate_hash_from_obj(obj: object) -> str:
    return generate_hash_from_bytes(dumps(obj))

def generate_hash_from_feature_collection(feat_coll: object) -> str:
    feat_coll_checksum = feat_coll.copy()
    feat_coll_checksum['timeStamp'] = None
    for f in feat_coll_checksum['features']:
        f['id'] = None

    return generate_hash_from_obj(feat_coll_checksum)

def generate_hash_from_bytes(content: bytes) -> str:
    readable_hash = hashlib.sha256(content).hexdigest()
    return 
