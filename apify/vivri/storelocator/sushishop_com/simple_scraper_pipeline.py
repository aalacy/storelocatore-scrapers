"""
This is a simple scraper library that builds on successive utility methods and user-defined lambdas and config,
to generate and run a full scraper.

It is generic in the sense it doesn't care about the source of data, nor how the fields are transformed.

The main entrypoint is `define_and_run`, but you can feel free to use any of the utilities therein individually.
"""

import csv
import simplejson as json
from simple_utils import *
from typing import *

MISSING = "<MISSING>"

def write_output(data: list, header: list):
    """
    Writes the header and data to a CSV.

    :param data:
        A list of fields, pre-sorted by their keys (matching the header keys)
    :param header:
        A list of pre-sorted column headers.
    :return:
        Nothing; it's a side-effecting method.
    """

    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(header)
        # Body
        for row in data:
            writer.writerow(row)

def missing_if_empty(field: str) -> str:
    """
    Convenience function that defaults an empty field to `MISSING`
    """
    if field == "":
        return MISSING
    else:
        return field


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
    Conveniently populates the fields in a SG record
    Defaults all fields to `MISSING`
    :rtype: dict
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


def decode_record (record: Dict[str, Dict], decode_map: dict, fail_on_outlier: bool, constant_fields: dict,
                   required_fields: list,
                   field_transform: dict = None) -> Optional[dict]:
    """
    Decodes a record, and returns a list of decoded string values, sorted by the record's own keys

    :param record:
        The raw record as a dict.
    :param decode_map:
        List of lists, each representing a path to search for a value. Results concatenated via a single space " ".
    :param constant_fields:
        Dict of constant values, to be present in the result.
    :param required_fields:
        List of fields that are mandatory.
    :param fail_on_outlier:
        Should the function except on missing a mandatory field, or just record an absence and skip it?
    :param field_transform:
        A map keyed on the logical field name, of a string->string lambda that transforms the field
    :return:
    """

    # instantiate with the constant fields
    result = constant_fields
    for field, fieldPaths in decode_map.items():

        field_value = ""
        for fieldPath in fieldPaths:
            next_value = drill_down_into(record, fieldPath)
            if next_value is not None:
                field_value += " " + str(next_value)

        field_value = field_value.strip() # remove prefixed space

        transformer = field_transform.get(field)
        if transformer is not None:
            field_value = transformer(field_value)

        if field_value == "":
            try:
                required_fields.index(field) # will only succeed if it's there
                print("Required field: " + field + " was missing from record: " + json.dumps(record))
                if fail_on_outlier:
                    raise Exception("Required field: " + field + " was missing from record: " + json.dumps(record))
                else:
                    return None
            except ValueError:
                # it's not in the required_field list, ergo it's defaultable.
                field_value = MISSING

        result[field] = missing_if_empty(field_value)

    return result


def parse_data(locations: List[Dict[str, str]],
               record_mapping: Dict[str, str],
               constant_fields: Dict[str, str],
               required_fields: List[str],
               fail_on_outlier: bool,
               field_transform: Dict[str, object],
               record_identity_fields: List[str],
               ) -> List[List[str]]:
    """
    Parses the raw location data

    :param locations:
        A list of raw location data (as dict).
    :param record_mapping:
        List of lists, each representing a path to search for a value. Results concatenated via a single space " ".
    :param constant_fields:
        Dict of constant values, to be present in the result.
    :param required_fields:
        List of fields that are mandatory.
    :param field_transform:
        A map keyed on the logical field name, of a string->string lambda that transforms the field
    :param fail_on_outlier:
        Should the function except on missing a mandatory field, or just record an absence and skip it?
    :param record_identity_fields:
        Fields, which together would create a unique identity for a record.
        Example: ["street_address", "city", "state"]
        If fields are empty, no deduping happens.
    :return:
        A list of location data, each record being a list of parsed string values, sorted by key.
    """

    result = []
    identities = set()

    for record in locations:
        decoded = decode_record(
            record=record,
            decode_map=record_mapping,
            constant_fields=constant_fields,
            required_fields=required_fields,
            field_transform=field_transform,
            fail_on_outlier=fail_on_outlier)

        if decoded is not None: # only append successfully decoded fields.

            # if we want to dedup based on identities
            if len(record_identity_fields) > 0:
                identity = record_id_function(record_identity_fields, decoded)
                if identity not in identities:
                    result.append(sort_values_dict(decoded))
                    identities.add(identity)
                else:
                    stderr(f"Duplicate record found with identity: {identity}")
            else:
                result.append(sort_values_dict(decoded))

    return result

def define_and_run(data_fetcher: lambda: List[Dict[str, str]],
                   record_mapping: dict,
                   constant_fields=None,
                   required_fields=None,
                   field_transform=None,
                   record_identity_fields=None,
                   fail_on_outlier=False):
    """
    Creates and executes the scraper pipeline.
    Writes `data.csv` to the current dir, and logs out useful info/errors.

    :param data_fetcher:
        A lambda that fetches a raw list of location data, each record being a dict. Can be deeply nested or flat.
    :param record_mapping:
        List of lists, each representing a path/ to search for a value in the fetched data rows. Results concatenated via a single space " ".
        Each key represents a field to be populated in the final results.

        For example: { locations: { street: "123 Sesame St.", addr2: "Unit #3" }}
        Could be parsed as: { street_address: [["locations", "street"], ["locations", "addr2"]] }
    :param constant_fields:
        Dict of constant values, to be present in the result.
        For example: { locator_domain: "https://windermere.com" }
        Defaults to empty dict.
    :param required_fields:
        List of fields that are mandatory.
        Defaults to ["street_address", "city", "state"]
    :param field_transform:
        A map keyed on the logical field name, of a string->string lambda that transforms the field.
        Defaults to empty dict.
    :param fail_on_outlier:
        Should the function except on missing a mandatory field, or just record an absence and skip it?
        Default is False.
    :param record_identity_fields:
        Fields, which together would create a unique identity for a record.
        Example: ["street_address", "city", "state"]
        If fields are empty, no deduping happens.
        Defaults to empty list.
    :return:
        Nothing, as it simply writes to a file.
    """

    if constant_fields is None:
        constant_fields = {}
    if required_fields is None:
        required_fields = ["street_address", "city", "state"]
    if field_transform is None:
        field_transform = {}
    if record_identity_fields is None:
        record_identity_fields = []

    csv_header = sorted_keys(record_mapping)
    csv_header.extend(sorted_keys(constant_fields))
    csv_header.sort()

    initial_data = data_fetcher()

    print(f"Number of initial records: {str(len(initial_data))}")

    data = parse_data(
        locations=initial_data,
        record_mapping=record_mapping,
        constant_fields=constant_fields,
        required_fields=required_fields,
        field_transform=field_transform,
        fail_on_outlier=fail_on_outlier,
        record_identity_fields=record_identity_fields
    )

    print(f"Number of valid records in resultset: {str(len(data))}")

    write_output(data, csv_header)
