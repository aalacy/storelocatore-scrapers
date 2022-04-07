from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
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


def fetch_records(search):
    with SgRequests() as session:
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
            for _ in locations:
                hours = []
                for hh in _["openingHours"].get("weekDayOpeningList", []):
                    times = "closed"
                    if not hh["closed"]:
                        times = f"{hh['openingTime']['formattedHour']}-{hh['closingTime']['formattedHour']}"
                    hours.append(f"{hh['weekDay']}: {times}")
                search.found_location_at(
                    _["geoPoint"]["latitude"],
                    _["geoPoint"]["longitude"],
                )
                street_address = _["address"]["line1"]
                if _["address"]["line2"]:
                    street_address += " " + _["address"]["line2"]
                yield SgRecord(
                    page_url=locator_domain + "/store/" + _["name"],
                    store_number=_["name"],
                    location_name=_["displayName"].replace("WOS", "").strip(),
                    street_address=street_address,
                    city=_["address"]["town"],
                    state=_["address"]["region"]["isocodeShort"],
                    zip_postal=_["address"]["postalCode"],
                    country_code=_["address"]["country"]["isocode"],
                    phone=_["address"]["phone"],
                    latitude=_["geoPoint"]["latitude"],
                    longitude=_["geoPoint"]["longitude"],
                    locator_domain=locator_domain,
                    location_type=_["baseStoreName"],
                    hours_of_operation="; ".join(hours),
                )
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


if __name__ == "__main__":
    with SgRequests() as http:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            for rec in fetch_records(search):
                writer.write_row(rec)
