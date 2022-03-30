from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("uni-mart")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://uni-mart.com"
base_url = "https://uni-mart.com/locations?radius=-1&filter_catid=0&limit=0&format=json&geo=1&limitstart=0&latitude={}&longitude={}"


def fetch_records(search):
    # Need to add dedupe. Added it in pipeline.
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        with SgRequests() as session:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            logger.info(("Pulling Geo Code %s..." % lat, lng))
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()[
                "features"
            ]
            total += len(locations)
            for _ in locations:
                addr = list(
                    bs(_["properties"]["fulladdress"], "lxml")
                    .select_one("span.locationaddress")
                    .stripped_strings
                )
                search.found_location_at(
                    _["geometry"]["coordinates"][1],
                    _["geometry"]["coordinates"][0],
                )
                yield SgRecord(
                    page_url=locator_domain + _["properties"]["url"],
                    store_number=_["properties"]["name"].split("#")[1],
                    location_name=_["properties"]["name"],
                    street_address=addr[0],
                    city=addr[1].split(",")[0],
                    state=addr[1].split(",")[1],
                    zip_postal=addr[2].split("\xa0")[1],
                    latitude=_["geometry"]["coordinates"][1],
                    longitude=_["geometry"]["coordinates"][0],
                    country_code=addr[2].split("\xa0")[0],
                    locator_domain=locator_domain,
                    raw_address=" ".join(addr).replace("\xa0", " "),
                )
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
