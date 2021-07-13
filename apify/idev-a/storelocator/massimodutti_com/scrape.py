from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("massimodutti")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.massimodutti.com/"
base_url = "https://www.massimodutti.com/itxrest/2/bam/store/34009456/physical-store?appId=1&languageId=-1&latitude={}&longitude={}&favouriteStores=true&lastStores=false&closerStores=true&min=10&radioMax=1000&receiveEcommerce=false&showBlockedMaxPackage=false"

days = [
    "",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


search = DynamicGeoSearch(
    country_codes=SearchableCountries.WITH_COORDS_ONLY,
    max_radius_miles=50,
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
            "closerStores"
        ]
        total += len(locations)
        for store in locations:
            hours = []
            for hr in store.get("openingHours", {}).get("schedule", []):
                times = f"{hr['timeStripList'][0]['initHour']}-{hr['timeStripList'][0]['initHour']}"
                for hh in hr["weekdays"]:
                    hours.append(f"{days[hh]}: {times}")
            search.found_location_at(
                store["latitude"],
                store["longitude"],
            )
            store["street"] = " ".join(store["addressLines"])
            store["zipcode"] = store["zipCode"] or "<MISSING>"
            store["state"] = store["state"] or "<MISSING>"
            store["city"] = store["state"] or "<MISSING>"
            store["hours"] = "; ".join(hours) or "<MISSING>"
            store["phone"] = "<MISSING>"
            if store.get("phones"):
                store["phone"] = store["phones"][0]
            yield store
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
            mapping=["zipcode"],
        ),
        country_code=sp.MappingField(
            mapping=["countryCode"],
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
