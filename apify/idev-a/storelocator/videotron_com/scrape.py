from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("videotron")

_headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://magasins.videotron.com/?q=montreal",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://videotron.com/"
base_url = "https://magasins.videotron.com/index.html?q={}"

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA], max_radius_miles=50
)


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for zip in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % zip))
        locations = session.get(base_url.format(zip), headers=_headers).json()[
            "locations"
        ]
        total += len(locations)
        for ss in locations:
            store = ss["loc"]
            hours = []
            for hh in store["hours"].get("days", []):
                times = "closed"
                if hh["intervals"]:
                    ii = hh["intervals"][0]
                    times = f"{_time(ii['start'])}-{_time(ii['start'])}"
                hours.append(f"{hh['day']}: {times}")
            search.found_location_at(
                store["latitude"],
                store["longitude"],
            )
            store["street"] = store["address1"]
            if store["address2"]:
                store["street"] += " " + store["address2"]
            store["hours"] = "; ".join(hours) or "<MISSING>"
            store["page_url"] = store["website"]["url"]
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
            mapping=["postalCode"],
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
