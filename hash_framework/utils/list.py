"""
Utilities for manipulating and printing lists.
"""

from typing import List, Optional


def prefix_list(obj: List[str], prefix: Optional[str]) -> List[str]:
    """
    Prefixes all items in a string list a given str.
    """
    assert isinstance(obj, list)
    assert prefix is None or isinstance(prefix, str)
    if prefix is None:
        return obj

    result = []
    for item in obj:
        assert isinstance(item, str)
        result.append(prefix + item)

    return result


def unprefix_list(obj: List[str], prefix: Optional[str]) -> List[str]:
    """
    Strips a specified prefix from all items in the string list.
    """
    assert isinstance(obj, list)
    assert prefix is None or isinstance(prefix, str)
    if prefix is None:
        return obj

    lprefix = len(prefix)
    result = []
    for item in obj:
        assert isinstance(item, str)
        if item.startswith(prefix):
            result.append(item[lprefix:])
        else:
            result.append(item)
    return result
