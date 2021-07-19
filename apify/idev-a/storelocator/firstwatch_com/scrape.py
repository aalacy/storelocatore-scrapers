from sgscrape import simple_scraper_pipeline as sp
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("firstwatch")

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.firstwatch.com"
base_url = "https://www.firstwatch.com/api/get_locations.php?latitude={}&longitude={}"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    expected_search_radius_miles=50,
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
        locations = session.get(base_url.format(lat, lng)).json()
        total += len(locations)
        for store in locations:
            if store["openstatus"] != "open":
                continue
            hours = []
            search.found_location_at(
                store["latitude"],
                store["longitude"],
            )
            store["street"] = store["address"]
            if store["address_extended"]:
                store["street"] += " " + store["address_extended"]
            store["hours"] = "; ".join(hours) or "<MISSING>"
            store["page_url"] = f"https://www.firstwatch.com/locations/{store['slug']}"
            h_list = bs(
                session.get(store["page_url"], headers=_headers).text, "lxml"
            ).find("script", {"id": "locations-detail"})
            hours_of_operation = SgRecord.MISSING
            if h_list != None:
                _hr = bs(h_list.string, "lxml").select("div.loc-item address")
                if len(_hr) > 1:
                    hours_of_operation = list(_hr[-1].stripped_strings)[0]
            store["hours"] = hours_of_operation
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
            mapping=["street"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["zip"],
        ),
        country_code=sp.ConstantField("US"),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["id"],
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
