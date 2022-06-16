from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("firstwatch")

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.firstwatch.com"
base_url = "https://www.firstwatch.com/api/locations.php?latitude={}&longitude={}"


def fetch_records(search):
    with SgRequests() as session:
        maxZ = search.items_remaining()
        total = 0
        for lat, lng in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            logger.info(("Pulling Geo Code %s..." % lat, lng))
            res = session.get(base_url.format(lat, lng), headers=_headers)
            if res.status_code != 200:
                continue
            locations = res.json()
            total += len(locations)
            for store in locations:
                location_type = ""
                if store["openstatus"] != "open":
                    location_type = store["openstatus"]
                search.found_location_at(
                    store["latitude"],
                    store["longitude"],
                )

                street_address = store["address"]
                if store.get("address_extended"):
                    street_address += " " + store["address_extended"]

                page_url = f"https://www.firstwatch.com/locations/{store['slug']}"
                logger.info(page_url)

                h_list = bs(
                    session.get(page_url, headers=_headers).text, "lxml"
                ).select_one("div.location-details-main-1 p")
                hours_of_operation = SgRecord.MISSING
                if h_list:
                    hours_of_operation = h_list.text.strip()

                yield SgRecord(
                    page_url=page_url,
                    location_name=store["name"],
                    store_number=store["id"],
                    street_address=street_address,
                    city=store["city"],
                    state=store["state"],
                    zip_postal=store["zip"],
                    country_code="US",
                    phone=store["phone"],
                    latitude=store["latitude"],
                    longitude=store["longitude"],
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )

            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_8()
    )

    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
