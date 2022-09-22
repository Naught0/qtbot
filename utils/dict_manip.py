from functools import reduce
from typing import Any, Hashable
from nltk.metrics import edit_distance as ed


def get_closest(word_dict, word):
    """returns the key which matches most closely to 'word'"""
    # stores keys and their edit distance values
    distance_dict = {}

    for key in word_dict:
        distance_dict[key] = ed(key, word)

    # return key w/ least edits
    return min(distance_dict, key=distance_dict.get)


def key_with_max_value(d):
    """
    a) create a list of the dict's keys and values;
    b) return the key with the max value
    Shamelessly taken from:
    http://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
    """
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(max(v))]


def key_with_min_value(d):
    """
    a) create a list of the dict's keys and values;
    b) return the key with the max value
    Shamelessly taken from:
    http://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
    """
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(min(v))]


def dig(d: dict, *keys, default=None) -> Any:
    """Dig for a value in a dictionary with an optionally configurable fallback value.
    Works similarly to ruby's `Hash#dig` method

    Args:
        d (dict)
        default (Any, optional): The value to return if the key is not found. Defaults to None.

    Returns:
        Any
    """

    def func(accum: dict, k: Hashable) -> Any:
        if not isinstance(accum, dict):
            raise TypeError
        return accum.get(k, default)

    try:
        return reduce(func, keys, d)
    # Ooo!! Ahh!! Bare except!
    except:
        return default
