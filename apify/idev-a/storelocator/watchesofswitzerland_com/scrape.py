from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("watchesofswitzerland")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.watchesofswitzerland.com"
base_url = (
    "https://www.watchesofswitzerland.com/store-finder?q=&latitude={}&longitude={}"
)

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
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
            "results"
        ]
        total += len(locations)
        for store in locations:
            hours = []
            for hh in store["openingHours"].get("weekDayOpeningList", []):
                times = "closed"
                if not hh["closed"]:
                    times = f"{hh['openingTime']['formattedHour']}-{hh['closingTime']['formattedHour']}"
                hours.append(f"{hh['weekDay']}: {times}")
            search.found_location_at(
                store["geoPoint"]["latitude"],
                store["geoPoint"]["longitude"],
            )
            store["lat"] = store["geoPoint"]["latitude"]
            store["lng"] = store["geoPoint"]["longitude"]
            store["street"] = store["address"]["line1"]
            if store["address"]["line2"]:
                store["street"] += " " + store["address"]["line2"]
            store["city"] = store["address"]["town"]
            store["state"] = store["address"]["region"]["isocodeShort"]
            store["zip_postal"] = store["address"]["postalCode"]
            store["country"] = store["address"]["country"]["isocode"]
            store["hours"] = "; ".join(hours) or "<MISSING>"
            store["phone"] = store["address"]["phone"]
            store["type"] = store["baseStoreName"]
            store["page_url"] = locator_domain + "/store/" + store["name"]
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
            mapping=["displayName"],
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
        location_type=sp.MappingField(
            mapping=["type"],
        ),
        store_number=sp.MappingField(
            mapping=["name"],
            part_of_record_identity=True,
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
