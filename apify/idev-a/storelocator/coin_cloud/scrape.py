from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord

logger = SgLogSetup().get_logger("coin")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.coin.cloud"
base_url = "https://www.coin.cloud/dcms"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA, SearchableCountries.BRAZIL],
    expected_search_radius_miles=100,
    use_state=False,
)


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    token = bs(session.get(base_url, headers=_headers).text, "lxml").select_one(
        "div#storerocket-widget"
    )["data-storerocket-id"]
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % lat, lng))
        url = f"https://api.storerocket.io/api/user/{token}/locations?lat={lat}&lng={lng}&radius=250"
        locations = session.get(url, headers=_headers).json()["results"]["locations"]
        total += len(locations)
        for _ in locations:
            street_address = _["address_line_1"]
            if _["address_line_2"]:
                street_address += " " + _["address_line_2"]
            hours = []
            hours.append(f"Mon: {_['mon']}")
            hours.append(f"Tue: {_['tue']}")
            hours.append(f"Wed: {_['wed']}")
            hours.append(f"Thu: {_['thu']}")
            hours.append(f"Fri: {_['fri']}")
            hours.append(f"Sat: {_['sat']}")
            hours.append(f"Sun: {_['sun']}")

            store = {}
            search.found_location_at(
                _["lat"],
                _["lat"],
            )
            store["name"] = _["name"]
            store["store_number"] = _["id"]
            store["lat"] = _["lat"]
            store["lng"] = _["lng"]
            store["street"] = street_address
            store["city"] = _["city"]
            store["state"] = _["state"]
            store["zip_postal"] = _.get("postcode")
            store["country"] = _["country"]
            store["hours"] = "; ".join(hours) or SgRecord.MISSING
            store["phone"] = _["phone"]
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["street"],
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
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["name"],
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
