"""
An eclectic collection of simple utilities.
"""

from __future__ import print_function
import sys
import time
import bs4
import urllib.parse
from typing import *

def stderr(*args, **kwargs):
    """
    prints to stderr
    """
    print(*args, file=sys.stderr, **kwargs)

def sorted_keys(the_dict: dict):
    """
    :returns
        The keys of the dict as a sorted list.
    """
    keys = []
    for k in the_dict.keys():
        keys.append(k)
    keys.sort()
    return keys

def sort_values_dict(the_dict: dict):
    """
    :returns
        The values in the dict as a list, sorted by the dict keys.
    """
    values = []
    for k in sorted_keys(the_dict):
        values.append(the_dict[k])

    return values

def drill_down_into(record: dict, field_chain: list):
    """
    Follows a `field_path` in the `record` dictionary.
    :returns
        The value in the `record` after traversing the `field_path`.
        If `field_path` == [], returns the record.
        If some key in the chain isn't found, returns `None`.
    """
    result = record
    for step in field_chain:
        try:
            result = result[step]
        except KeyError:
            result = None
            break
    return result

def ms_since_epoch() -> int:
    """
    :return: Millis since epoch, rounded down to second.
    """
    return int(time.time() * 1000)

def merge_ar(ar: list, sep = "") -> str:
    """
    Merges a list into a string, given a separator
    merge_ar([]) == ''
    merge_ar([1, 2], "~") == '1~2'
    """
    res = ""
    for x in ar:
        if res != "":
            res += sep
        res += str(x)
    return res


def xml_to_dict_one_level_deep(location_xml: bs4.Tag) -> dict:
    """
    Returns the 1-level-deep dictionary representation of a bs4.Tag xml element.
    """
    return {child.name: urllib.parse.unquote(child.text) for child in location_xml.findChildren()}

def apply_in_seq(fns: List[lambda s: object], s: object) -> object:
    """
    Applies the provided functions to the input in a sequence, producing the result
    It may be useful to partially apply to create a single lambda, e.g.:
    `final_lambda = partial(apply_in_seq, [lambda_a, lambda_b, ...])`
    """
    res = s
    for fn in fns:
        res = fn(res)
    return res


def extract_country_code_common_n_a_mappings(default_if_empty: str, initial_country_code: str) -> str:
    """
    Provides some common occurrences of N.American mappings (for: CA, US)
    """
    return extract_coutry_code(
        country_code_mappings = {
            "canada": "CA",
            "usa": "US",
            "u.s.a.": "US",
            "u.s.a": "US",
            "united states": "US",
            "united-states": "US",
        },
        default_if_empty=default_if_empty,
        initial_country_code=initial_country_code
    )


def extract_coutry_code(country_code_mappings: Dict[str,str], default_if_empty: str, initial_country_code: str) -> str:
    """
    Extracts the country code based on the following input:
    :param country_code_mappings: A list of known country to country-code mappings, keys being in lowercase.
    :param default_if_empty: Default value if the `initial_country_code.strip()` is an empty string.
    :param initial_country_code: The string to match against the following rules.
            If it's length==2, we assume it's a valid code, and pass through as is.
    """
    if initial_country_code.strip() == "":
        return default_if_empty
    if len(initial_country_code) is 2: # proper country code
        return initial_country_code
    else:
        c_code = country_code_mappings.get(initial_country_code.lower())
        if c_code is None:
            return ""
        else:
            return c_code

def record_id_function(fields: List[str], record: dict) -> str:
    """
    Generates a human-readable string identity for a record based on the provided fields
    """
    ident = ""
    for f in fields:
        ident +=f"[{f}:{record.get(f)}]"
    return ident

def dedup_records(data: List[dict], record_identity: lambda r: str) -> List[dict]:
    """
    De-duplicating records based on an identity function.
    Choosing the first occurrence in the list.
    """
    identities = set()
    deduped = []
    for record in data:
        id = record_identity(record)
        if id not in identities:
            deduped.append(record)
    return deduped