from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord

logger = SgLogSetup().get_logger("caliber")

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "origin": "https://www.caliber.com",
    "referer": "https://www.caliber.com/find-a-location",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.caliber.com"
base_url = "https://www.caliber.com/api/es/search"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    expected_search_radius_miles=50,
    use_state=False,
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


def data(lat, lng):
    return {
        "size": "60",
        "query": {
            "bool": {
                "must": {
                    "query_string": {
                        "query": "+contentType:Center +(Center.serviceType:*)"
                    }
                },
                "filter": {
                    "geo_distance": {
                        "distance": "80.4672km",
                        "center.latlong": {"lat": str(lat), "lon": str(lng)},
                    }
                },
            }
        },
    }


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % lat, lng))

        locations = session.post(
            base_url, headers=_headers, json=data(lat, lng)
        ).json()["contentlets"]
        total += len(locations)
        for store in locations:
            hours = []
            if store.get("mondayHoursOpen"):
                hours.append(
                    f"Mon: {store['mondayHoursOpen'].split(' ')[-1]}-{store['mondayHoursClose'].split(' ')[-1]}"
                )
                hours.append(
                    f"Tue: {store['tuesdayHoursOpen'].split(' ')[-1]}-{store['tuesdayHoursClose'].split(' ')[-1]}"
                )
                hours.append(
                    f"Wed: {store['wednesdayHoursOpen'].split(' ')[-1]}-{store['wednesdayHoursClose'].split(' ')[-1]}"
                )
                hours.append(
                    f"Thu: {store['thursdayHoursOpen'].split(' ')[-1]}-{store['thursdayHoursClose'].split(' ')[-1]}"
                )
                hours.append(
                    f"Fri: {store['fridayHoursOpen'].split(' ')[-1]}-{store['fridayHoursClose'].split(' ')[-1]}"
                )
                if store.get("saturdayHoursOpen") and store.get("saturdayHoursClose"):
                    hours.append(
                        f"Sat: {store['saturdayHoursOpen'].split(' ')[-1]}-{store['saturdayHoursClose'].split(' ')[-1]}"
                    )
                else:
                    hours.append("Sat: Closed")
                if store.get("sundayHoursOpen") and store.get("sunHoursClose"):
                    hours.append(
                        f"Sat: {store['sundayHoursOpen'].split(' ')[-1]}-{store['sundayHoursClose'].split(' ')[-1]}"
                    )
                else:
                    hours.append("Sun: Closed")

            store["street"] = store["address1"]
            if store.get("address2") and store["address2"] != store["address1"]:
                store["street"] += " " + store["address2"]
            store["hours"] = "; ".join(hours) or SgRecord.MISSING
            store["page_url"] = locator_domain + store["urlMap"]
            location_type = []
            for tt in store["serviceType"]:
                location_type.append(" ".join(tt.keys()))
            store["location_type"] = ", ".join(location_type) or SgRecord.MISSING
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
            mapping=["title"],
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
            mapping=["telephone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(
            mapping=["location_type"],
        ),
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
