from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("watchesofswitzerland")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://uni-mart.com"
base_url = "https://uni-mart.com/locations?radius=-1&filter_catid=0&limit=0&format=json&geo=1&limitstart=0&latitude={}&longitude={}"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    expected_search_radius_miles=500,
)


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % lat, lng))
        locations = session.get(base_url.format(lat, lng), headers=_headers).json()[
            "features"
        ]
        total += len(locations)
        for _ in locations:
            store = {}
            addr = list(
                bs(_["properties"]["fulladdress"], "lxml")
                .select_one("span.locationaddress")
                .stripped_strings
            )
            search.found_location_at(
                _["geometry"]["coordinates"][1],
                _["geometry"]["coordinates"][0],
            )
            store["store_number"] = _["properties"]["name"].split("#")[1]
            store["name"] = _["properties"]["name"]
            store["street_address"] = addr[0]
            store["city"] = addr[1].split(",")[0]
            store["state"] = addr[1].split(",")[1]
            store["zip_postal"] = addr[2].split("\xa0")[1]
            store["latitude"] = _["geometry"]["coordinates"][1]
            store["longitude"] = _["geometry"]["coordinates"][0]
            store["country_code"] = addr[2].split("\xa0")[0]
            store["page_url"] = locator_domain + _["properties"]["url"]
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["page_url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["zip_postal"],
        ),
        country_code=sp.MappingField(
            mapping=["country_code"],
        ),
        phone=sp.MissingField(),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["store_number"],
        ),
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
