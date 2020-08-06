"""
This is a simple scraper library that builds on successive utility methods and user-defined lambdas and config,
to generate and run a full scraper.

It is generic in the sense it doesn't care about the source of data, nor how the fields are transformed.

The main entrypoint is `define_and_run`, but you can feel free to use any of the utilities therein individually.
"""

import csv
import simplejson as json

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

def missing_if_empty(field: str):
    """
    Convenience function that defaults an empty field to `MISSING`
    """
    if field == "":
        return MISSING
    else:
        return field

def decode_record (record: dict, decode_map: dict, fail_on_outlier: bool, constant_fields: dict, required_fields: list, field_transform=None):
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
        else:
            transformer = field_transform.get(field)
            if transformer is not None:
                field_value = transformer(field_value)

        result[field] = missing_if_empty(field_value)

    return sort_values_dict(result)


def parse_data(locations: list, record_mapping: dict, constant_fields: dict, required_fields: list, fail_on_outlier: bool, field_transform: list):
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
    :return:
        A list of location data, each record being a list of parsed string values, sorted by key.
    """

    print("Number of locations in resultset: " + str(len(locations)))

    result = []
    for record in locations:
        decoded = decode_record(
            record=record,
            decode_map=record_mapping,
            constant_fields=constant_fields,
            required_fields=required_fields,
            field_transform=field_transform,
            fail_on_outlier=fail_on_outlier)

        if decoded is not None:
            # only append successfully decoded fields.
            result.append(decoded)

    return result

def define_and_run(data_fetcher: lambda: list, record_mapping: dict, constant_fields=None, required_fields=None, field_transform=None, fail_on_outlier=False):
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
    :return:
        Nothing, as it simply writes to a file.
    """

    if constant_fields is None:
        constant_fields = {}
    if required_fields is None:
        required_fields = ["street_address", "city", "state"]
    if field_transform is None:
        field_transform = {}


    csv_header = sorted_keys(record_mapping)
    csv_header.extend(sorted_keys(constant_fields))
    csv_header.sort()

    data = parse_data(
        locations=data_fetcher(),
        record_mapping=record_mapping,
        constant_fields=constant_fields,
        required_fields=required_fields,
        field_transform=field_transform,
        fail_on_outlier=fail_on_outlier)

    write_output(data, csv_header)
