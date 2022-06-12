from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("colormemine")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://www.colormemine.com/"


def fetch_records(search):
    # Need to add dedupe. Added it in pipeline.
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        with SgRequests() as session:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            logger.info(("Pulling Geo Code %s..." % lat, lng))
            url = f"https://www.colormemine.com/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}&max_results=25&search_radius=2000"
            locations = session.get(url, headers=headers).json()
            total += len(locations)
            for _ in locations:
                if _["country"].lower() == "korea":
                    continue
                search.found_location_at(
                    _["lat"],
                    _["lng"],
                )
                hours = []
                if _["hours"]:
                    for hh in bs(_["hours"], "lxml").select("tr"):
                        hours.append(
                            f"{hh.select('td')[0].text}: {hh.select('td')[1].text}"
                        )

                street_address = _["address"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                yield SgRecord(
                    page_url=_["url"],
                    location_name=_["store"],
                    store_number=_["id"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    country_code=_["country"],
                    phone=_["phone"],
                    latitude=_["lat"],
                    longitude=_["lng"],
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
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
        )
        for rec in fetch_records(search):
            writer.write_row(rec)
