#!/usr/bin/python

class HashState:
    hashes = {
        "md4":
            {
                "blocksize": 512,
                "state": 128,
                "intermediate": 1536,
                "bits": 32,
                "output_prefix": ['oaa', 'obb', 'occ', 'odd']
            }
    }

    function = "md4"
    algo = hashes[function]

    args = {}

    prefix = ""

    def __init__(self, fun="md4"):
        self.function = fun
        self.args = self.hashes[fun]
