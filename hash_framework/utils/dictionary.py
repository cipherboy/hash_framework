"""
Utilities for manipulating and printing dictionaries.
"""

from typing import List, Optional


def prefix_keys(obj: dict, prefix: Optional[str]) -> dict:
    """
    Prefixes all keys in a dictionary with a given str.
    """
    assert isinstance(obj, dict)
    assert prefix is None or isinstance(prefix, str)
    if prefix is None:
        return obj

    result = {}
    for key in obj:
        result[prefix + str(key)] = obj[key]

    return result


def unprefix_keys(obj: dict, prefix: Optional[str]) -> dict:
    """
    Strips a specified prefix from all keys in the dictionary.
    """
    assert isinstance(obj, dict)
    assert prefix is None or isinstance(prefix, str)
    if prefix is None:
        return obj

    result = {}
    for key in obj:
        if key.startswith(prefix):
            result[key[len(prefix) :]] = obj[key]
        else:
            result[key] = obj[key]
    return result


def print_dict(obj: dict, name: str):
    """
    Print out a dictionary with a specified name.
    """
    assert isinstance(obj, dict)
    assert isinstance(name, str)

    print("===begin " + name + "===")
    for key in obj:
        print("\t" + str(key) + ": " + str(obj[key]))
    print("===end " + name + "===")


def merge_dict(objs: List[dict]) -> dict:
    """
    Merge multiple dictionaries with unique keys.
    """
    assert isinstance(objs, (list, tuple))
    assert all(map(lambda x: isinstance(x, dict), objs))
    assert objs

    result: dict = {}
    for obj in objs:
        for key in obj:
            assert key not in result
            result[key] = obj[key]
    return result
