from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch
from sglogging import SgLogSetup

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


def fetch_records(search):
    with SgRequests() as session:
        maxZ = search.items_remaining()
        total = 0
        for lat, lng in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            logger.info(("Pulling Geo Code %s..." % lat, lng))

            try:
                locations = session.post(
                    base_url, headers=_headers, json=data(lat, lng)
                ).json()["contentlets"]
            except:
                continue
            total += len(locations)
            for store in locations:
                search.found_location_at(store["latitude"], store["longitude"])
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
                    if store.get("saturdayHoursOpen") and store.get(
                        "saturdayHoursClose"
                    ):
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

                street_address = store["address1"]
                if store.get("address2") and store["address2"] != store["address1"]:
                    street_address += " " + store["address2"]
                page_url = locator_domain + store["urlMap"]
                location_type = []
                for tt in store["serviceType"]:
                    location_type.append(" ".join(tt.keys()))
                yield SgRecord(
                    page_url=page_url,
                    location_name=store["title"],
                    street_address=street_address,
                    city=store["city"],
                    state=store["state"],
                    zip_postal=store["zip"],
                    country_code="USA",
                    phone=store.get("telephone"),
                    latitude=store["latitude"],
                    longitude=store["longitude"],
                    location_type=", ".join(location_type),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )

            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


if __name__ == "__main__":
    search = DynamicGeoSearch(country_codes=["us"], expected_search_radius_miles=500)
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
