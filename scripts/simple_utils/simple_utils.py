"""
An eclectic collection of simple utilities.
"""

from __future__ import print_function
import sys
import time
import bs4
import urllib.parse
from typing import *
from dill.source import getsource
from concurrent.futures import *
import json
# import eta as eta_lib

MISSING = '<MISSING>'

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

def dedup_records(data: list, record_identity: lambda r: str) -> list:
    """
    De-duplicating records based on an identity function.
    Choosing the first occurrence in the list.
    """
    identities = set()
    for record in data:
        id = record_identity(record)
        if id not in identities:
            identities.add(record)
            yield record

def remove_non_ascii(s: str) -> str:
    return s.encode('ascii', 'ignore').decode('ascii').strip()

def or_else(cond: str, default: str) -> str:
    return cond if cond else default

def or_missing(get_prop: lambda: str) -> str:
    try:
        prop = get_prop().strip()
        return prop if prop else MISSING
    except:
        return MISSING

def t (op: lambda: object, threshold: float = 0.5):
    """
    Time the lambda execution, and print out the function (via magic!) if the time is over the threshold (in secs)
    :return whatever `op` returns.
    """
    src = getsource(op).strip().replace("\n", " ")[0:77] + "..."
    t1 = time.clock_gettime(0)
    ret = op()
    t2 = time.clock_gettime(0)
    took = t2-t1
    if took > threshold:
        print (f"Took: {took} [{src}]")
    return ret

def split_list(n: int, original: list) -> Tuple[list, list]:
    """
    Splits a list at the n-th index, returning the left and right sides as a tuple.
    """
    return original[0:n], original[n:]

def json_objects_to_arr(original: Iterator) -> Generator:
    """
    Converts a string/char-iterator of json objects into a generator of dicts.
    "{a:b}{c:d}" -> [{a:b}, {c:d}]
    """
    curly_stack = 0
    cur_json = ""
    in_string = False
    for char in original:
        if not in_string and char == '{':
            curly_stack += 1
        elif not in_string and char == '}':
            curly_stack -= 1
        elif char == '"':
            in_string = not in_string
        else:
            pass

        cur_json += char

        if curly_stack == 0:
            yield json.loads(cur_json)
            cur_json = ""

def parallelize(search_space: list,
                fetch_results_for_rec: lambda x: list,
                id_func = None,
                processing_function = None,
                max_threads: int = 8,
                thread_prefix: str = 'parallelize') -> Generator:
    """
    Trivially parallelize any task that yields the GIL, such as I/O. A good example would be HTTP requests.
    The function uses `ThreadPoolExecutor` under the hood.

    For memory-utilization issues with large datasets, this function takes care of 3 parts:
    1) Asynchronously fetching results, using the search_space.
    2) Processing said results.
    3) Using an optional identity function to deduplicate the resultset.

    :param search_space: The data, on which the search will be performed. For example, coords, zip-codes, website lists.
    :param fetch_results_for_rec: Taking one datum from the `search_space`, this function retrieves a list of records.
    :param id_func: If present, is a function that accepts one record from `fetch_results_from_rec`, and returns its
                    unique, hashable id..
                    If it's present, it's used to dedup the records on the fly.
    :param processing_function: Transforms the each record, as received from each call to `fetch_results_for_rec`.
                                Defaults to record identity in implementation.
    :param max_threads: The maximum number of threads in the thread-pool (also, the chunk-size in the underlying algo).
    :param thread_prefix: The prefix to name the threads in the threadpool, for debugging purposes.

    :return: Yields computed and possibly deduped records from `fetch_results_from_rec` , one by one.
    """
    with ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix=thread_prefix) as executor:
        ids = set()
        next_chunk, rest = split_list(max_threads, search_space)
        while next_chunk:
            for res in executor.map(fetch_results_for_rec, next_chunk):
                processed_results = t(lambda: processing_function(res), 0.1) if processing_function else [res]
                for processed in processed_results:
                    if id_func:
                        rec_id = id_func(processed)
                        if rec_id in ids:
                            continue
                        else:
                            ids.add(rec_id)
                            yield processed
                    else:
                        yield processed

            next_chunk, rest = split_list(max_threads, rest)

def find_cusp(left_domain: int, right_domain: int, process_fn):
    """
    For a function `f(r)` similar to the form: f(r) = min(a, b-r), which is to say: it is constant on the left,
    then starts descending at some point going right;

    This function finds the cusp (point where the plateau ends) and returns it.

    This is very useful in locating the maximum radius of a search-API that returns location results, but silently stops
    returning new results at some point. The domain, in this case, would be the search radius, and it plateaus on the
    left (small radii), where all stores are returned. Then, the store count drops, as the search API stops matching
    the provided radius.

    One intended usage is to run this function during development, to be able to find and plug the max radius into the
    production-run of a location webscraper.

    :param left_domain: The smallest value of the search domain (e.g. search-radius)
    :param right_domain: The largest value of the search domain (e.g. search-radius)
    :param process_fn: Calculates (and returns) the number of results based on the domain (e.g. number of nationwide
                       stores based on search radius)
    :return: The cusp point in the domain, as discussed above.
    """

    if right_domain - left_domain <= 1: # adjacent or merged points on domain
        print(f"Exhausted search on: {left_domain}")
        return left_domain

    mid_domain = int((left_domain + right_domain) / 2)
    mid_result = process_fn(mid_domain)

    mid_result_left = process_fn(mid_domain - 1) if mid_domain - 1 >= left_domain else mid_result - 1
    mid_result_right = process_fn(mid_domain + 1) if mid_domain + 1 <= right_domain else mid_result + 1

    # still need to find the cusp; go left
    if mid_result < mid_result_left:
        print(f"<- L {left_domain} R {mid_domain} mid: {mid_result} mid-L: {mid_result_left} mid-R: {mid_result_right}")
        return find_cusp(left_domain=left_domain, right_domain=mid_domain, process_fn=process_fn)

    # passed the cusp; go right
    if mid_result == mid_result_right:
        print(f"-> L {mid_domain} R {right_domain} mid: {mid_result} mid-L: {mid_result_left} mid-R: {mid_result_right}")
        return find_cusp(left_domain=mid_domain, right_domain=right_domain, process_fn=process_fn)

    # found the cusp!
    if mid_result == mid_result_left:
        print(f"! {mid_domain}")
        return mid_domain

    raise Exception(f"IMPOSSIBLE! L: {mid_result_left} M: {mid_result} R: {mid_result_right}")


def sg_record(page_url: str = MISSING,
              location_name: str = MISSING,
              street_address: str = MISSING,
              city: str = MISSING,
              state: str = MISSING,
              zip_postal: str = MISSING,
              country_code: str = MISSING,
              store_number: str = MISSING,
              phone: str = MISSING,
              location_type: str = MISSING,
              latitude: str = MISSING,
              longitude: str = MISSING,
              locator_domain: str = MISSING,
              hours_of_operation: str = MISSING) -> dict:
    """
    Conveniently populates the fields in a SG record, returning a `dict`.
    Defaults all fields to `MISSING`
    """
    return {
        "page_url": page_url,
        "location_name": location_name,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip": zip_postal,
        "country_code": country_code,
        "store_number": store_number,
        "phone": phone,
        "location_type": location_type,
        "latitude": latitude,
        "longitude": longitude,
        "locator_domain": locator_domain,
        "hours_of_operation": hours_of_operation
    }
