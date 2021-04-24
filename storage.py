
from typing import Dict, Any

# Manager for the JSON storage data

class JSONData:
    data: Dict[str, Any]

    def __init__(self, data):
        self.data = data

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, v):
        self.data[idx] = v

    def __contains__(self, idx):
        return idx in self.data
