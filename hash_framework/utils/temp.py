"""
Utilities for manipulating temporary directories
"""

import tempfile

def tmp_dir():
    return tempfile.TemporaryDirectory(prefix="hash_framework")
