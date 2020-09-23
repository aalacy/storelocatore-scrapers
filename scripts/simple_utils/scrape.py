from simple_scraper_pipeline import SimpleScraperPipeline
import simple_network_utils as sg_net
import simple_utils as sg_util
from typing import *


def fetch_data() -> List[dict]:
    """
    This function will fetch results from a remote source, returning a list of dicts, each representing a record.

    For your convenience, we have included three functions to handle network traffic:
    - fetch_data: Simply wraps a network call, raising an exception if not successful.
    - fetch_xml: If the response is in XML, use this convenience method.
    - fetch_json: If the response is in JSON, use this convenience method.

    This function may do any of the following:
    - Do a single call, returning the list.
    - Do multiple calls in succession, yielding each record value.
    - Use sgzip, sggrid or (coord_)for_radius to traverse a geographical space, yielding each record value.
    - Anything else, as long as each record value is yielded.

    Yielding a value instead of returning a list will guarantee you'll see `data.csv` populated incrementally,
    as well as see useful running statistics.
    """
    pass

def scrape():
    """
    Instead of procedurally scraping the website, let's use SimpleScraperPipeline to define our scrape.
    """

    # Data mappers
    record_mapping = {
        "page_url": ["path", "to", "record", "in", "dict", "from", "fetch_data"],
        "location_name": [],
        "street_address": [],
        "city": [],
        "state": [],
        "zip": [],
        "country_code": [],
        "store_number": [],
        "phone": [],
        "location_type": [],
        "latitude": [],
        "longitude": [],
        "hours_of_operation": []
    }

    # Those fields are constant, and will have no mappings
    constant_fields = {
        "locator_domain": "YOUR_DOMAIN",
    }

    # Fail record ingestion if any of these isn't present.
    required_fields = [
        "street_address",
        "city",
        "state"
    ]

    # Does the entire scrape fail if any individual record fails to be transformed.
    fail_on_outliers = False

    # do you need to transform any fields after extracting from the result dict?
    field_transformers = {
        "field_name": lambda s: s,
    }

    pipeline = SimpleScraperPipeline(scraper_name="YOUR_DOMAIN",
                                     data_fetcher=fetch_data,
                                     record_mapping=record_mapping,
                                     constant_fields=constant_fields,
                                     required_fields=required_fields,
                                     field_transform=field_transformers,
                                     fail_on_outlier=fail_on_outliers)

    pipeline.run()

if __name__ == "__main__":
    scrape()