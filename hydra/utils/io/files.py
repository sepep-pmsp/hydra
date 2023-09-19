import json
import os

def read_json(file, path=None):
    if path:
        file = os.path.join(path, file)
    with open(file) as f:
        return json.load(f)
    