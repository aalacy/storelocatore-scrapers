from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("colormemine")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://www.colormemine.com/"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    maximum_search_radius=None,
    max_search_results=None,
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
        url = f"https://www.colormemine.com/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}&max_results=25&search_radius=2000"
        locations = session.get(url, headers=headers, timeout=15).json()
        total += len(locations)
        for loc in locations:
            if loc["country"].lower() == "korea":
                continue
            search.found_location_at(
                loc["lat"],
                loc["lng"],
            )
            hours = []
            if loc["hours"]:
                for hh in bs(loc["hours"], "lxml").select("tr"):
                    hours.append(
                        f"{hh.select('td')[0].text}: {hh.select('td')[1].text}"
                    )

            loc["hours_of_operation"] = "; ".join(hours)
            loc["street_address"] = loc["address"]
            if loc["address2"]:
                loc["street_address"] += " " + loc["address2"]
            yield loc
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["store"],
        ),
        store_number=sp.MappingField(
            mapping=["id"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
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
            mapping=["zip"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours_of_operation"]),
        location_type=sp.MissingField(),
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
