from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord

logger = SgLogSetup().get_logger("7eleven")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.7eleven.co.th"
base_url = "https://7eleven-api-prod.jenosize.tech/v1/Store/GetStoreByCurrentLocation"

search = DynamicGeoSearch(country_codes=[SearchableCountries.THAILAND], use_state=False)


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_country="us", proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % lat, lng))
        data = {"latitude": str(lat), "longitude": str(lng)}
        locations = session.post(base_url, headers=_headers, json=data).json()["data"]
        total += len(locations)
        for store in locations:
            store["street"] = store["address"]
            if store.get("province"):
                store["street"] = (
                    store["address"].replace(store["province"], "").strip()
                )
            store["phone"] = (
                store["tel"].split()[0] if store.get("tel") else SgRecord.MISSING
            )
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.ConstantField("https://www.7eleven.co.th/find-store"),
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
        city=sp.MissingField(),
        state=sp.MappingField(
            mapping=["province"],
        ),
        zipcode=sp.MappingField(
            mapping=["postcode"],
        ),
        country_code=sp.ConstantField("Thailand"),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["id"],
        ),
        raw_address=sp.MappingField(
            mapping=["address"],
        ),
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
