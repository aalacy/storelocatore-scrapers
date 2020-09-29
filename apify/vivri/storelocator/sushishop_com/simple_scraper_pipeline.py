import csv
from logging import Logger

import simplejson as json
from simple_utils import *
from typing import *
from sglogging import sglog
import time

class SimpleScraperPipeline:
    """
    This is a simple scraper framework that aims to be generic enough for most common scenarios.

    It is generic in the sense it doesn't care about the source of data, nor how the fields are transformed.
    """

    MISSING = "<MISSING>"

    def __init__(self,
                 scraper_name: str,
                 data_fetcher: lambda: List[dict],
                 record_mapping: Dict[str, List[List[str]]],
                 constant_fields=None,
                 required_fields=None,
                 field_transform=None,
                 record_identity_fields=None,
                 fail_on_outlier=False):
        """
        Creates and the scraper pipeline.
        Writes `data.csv` to the current dir, and logs out useful info/errors.

        :param scraper_name:
            The name of this scraper, as will appear in log prefixes.
        :param data_fetcher:
            A lambda that fetches a raw list of location data, each record being a dict. Can be deeply nested or flat.
            Preferably, the `data_fetcher` returns a Generator by means of yielding the data. The rest of the pipeline
            is built to stream data all the way to the file, allowing for incremental writes.
        :param record_mapping:
            A dict of lists, each key representing a field to be populated in the final results, and the lists
            representing a path to search for a value in the fetched data rows. For example:
            { street_address: ["locations", "street"] } will drill down to: { locations: { street: "123 Sesame St."}}

            Alternatively, if there are several places, which form a field, the mapping could be several lists, the
            results of which are concatenated by a single space: " ".
            For example: { locations: { street: "123 Sesame St.", addr2: "Unit #3" }}
            Will be parsed by mappings: { street_address: [["locations", "street"], ["locations", "addr2"]] }
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


        self.__log = sglog.SgLogSetup().get_logger(logger_name=scraper_name)

        self.__data_fetcher = data_fetcher
        self.__record_mapping = self.__normalize_mappings(record_mapping)

        self.__constant_fields = constant_fields
        self.__required_fields = required_fields
        self.__field_transform = field_transform
        self.__record_identity_fields = record_identity_fields
        self.__fail_on_outlier = fail_on_outlier


    def run(self) -> None:
        """
        Runs the framework,
        :return:
        """
        csv_header = sorted_keys(self.__record_mapping)
        csv_header.extend(sorted_keys(self.__constant_fields))
        csv_header.sort()

        start_sec = time.time()
        counter = 0

        with open('data.csv', mode='w') as output_file:
            writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            # Header
            writer.writerow(csv_header)

            initial_data = self.__data_fetcher()

            data = self.__parse_data(
                locations=initial_data,
                record_mapping=self.__record_mapping,
                constant_fields=self.__constant_fields,
                required_fields=self.__required_fields,
                field_transform=self.__field_transform,
                fail_on_outlier=self.__fail_on_outlier,
                record_identity_fields=self.__record_identity_fields
            )

            # Body
            for row in data:
                counter += 1
                if counter % 100 == 0:
                    self.__log.debug(f"Processed {counter} records...")

                writer.writerow(row)

        end_sec = time.time()

        self.__log.debug(f"Scrape stats: [took {str(end_sec - start_sec).split('.')[0]} seconds] [{counter} records]")


    def replace_logger(self, logger: Logger) -> None:
        """
        Replaces the default logger with another one.
        """
        self.__log = logger

    def __normalize_mappings(self, record_mapping: Dict[str, list]) -> Dict[str, List[List[str]]]:
        """
        Normalizes mappings to the nested list form, for both the single and the nested variants.
        """
        normalized = {}
        for k in record_mapping.keys():
            mapping = record_mapping[k]
            if isinstance(mapping[0], list):
                normalized[k] = mapping
            else:
                # that means we need to wrap
                normalized[k] = [mapping]
        return normalized

    def __missing_if_empty(self, field: str) -> str:
        """
        Convenience function that defaults an empty field to `MISSING`
        """
        if not field:
            return SimpleScraperPipeline.MISSING
        else:
            return field


    def __decode_record (self, record: dict, decode_map: dict, fail_on_outlier: bool, constant_fields: dict,
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
                    self.__log.info("Skipping record. Required field: " + field + " was missing from record: " + json.dumps(record))
                    if fail_on_outlier:
                        raise Exception("Required field: " + field + " was missing from record: " + json.dumps(record))
                    else:
                        return None
                except ValueError:
                    # it's not in the required_field list, ergo it's defaultable.
                    field_value = SimpleScraperPipeline.MISSING

            result[field] = self.__missing_if_empty(field_value)

        return result


    def __parse_data(self,
                     locations: List[dict],
                     record_mapping: Dict[str, List[List[str]]],
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

        identities = set()

        for record in locations:
            decoded = self.__decode_record(
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
                        yield sort_values_dict(decoded)
                        identities.add(identity)
                    else:
                        self.__log.debug(f"Duplicate record found with identity: {identity}")
                else:
                    yield sort_values_dict(decoded)
