from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("deadriver.com")

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "origin": "https://www.deadriver.com",
    "Host": "www.deadriver.com",
    "referer": "https://www.deadriver.com/contact-us",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}

locator_domain = "https://www.deadriver.com/"
page_url = "https://www.deadriver.com/contact-us"

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for code in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Zip Code %s..." % code))
        url = "https://www.deadriver.com/LocationFinder.asmx/GetLocation"
        data = {"zipCode": str(code)}
        res = session.post(url, headers=headers, json=data, timeout=15).json()
        if not res["d"]:
            continue
        locations = json.loads(res["d"])
        total += len(locations)
        for store in locations:
            search.found_location_at(
                store["Latitude"],
                store["Longitude"],
            )
            store["street"] = store["AddressOne"]
            if store["AddressTwo"]:
                store["street"] += ", " + store["AddressTwo"]
            store["country"] = "US"
            yield store
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.ConstantField(page_url),
        location_name=sp.MappingField(
            mapping=["CompanyName"],
        ),
        latitude=sp.MappingField(
            mapping=["Latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["Longitude"],
        ),
        street_address=sp.MappingField(
            mapping=["street"],
        ),
        city=sp.MappingField(
            mapping=["City"],
        ),
        state=sp.MappingField(
            mapping=["State"],
        ),
        zipcode=sp.MappingField(
            mapping=["ZipCode"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["PhoneOne"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MissingField(),
        store_number=sp.MissingField(),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
