from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("deadriver.com")

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "origin": "https://www.deadriver.com",
    "Host": "www.deadriver.com",
    "referer": "https://www.deadriver.com/contact-us",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}

locator_domain = "https://www.deadriver.com/"
page_url = "https://www.deadriver.com/contact-us"


def fetch_records(search):
    # Need to add dedupe. Added it in pipeline.
    with SgRequests() as session:
        maxZ = search.items_remaining()
        total = 0
        for code in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            logger.info(("Pulling Zip Code %s..." % code))
            url = "https://www.deadriver.com/LocationFinder.asmx/GetLocation"
            data = {"zipCode": str(code)}
            res = session.post(url, headers=headers, json=data).json()
            if not res["d"]:
                continue
            locations = json.loads(res["d"])
            total += len(locations)
            for _ in locations:
                search.found_location_at(
                    _["Latitude"],
                    _["Longitude"],
                )
                street_address = _["AddressOne"]
                if _["AddressTwo"]:
                    street_address += ", " + _["AddressTwo"]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["CompanyName"],
                    street_address=street_address,
                    city=_["City"],
                    state=_["State"],
                    zip_postal=_["ZipCode"],
                    country_code="US",
                    phone=_["PhoneOne"],
                    latitude=_["Latitude"],
                    longitude=_["Longitude"],
                    locator_domain=locator_domain,
                )
                progress = (
                    str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
                )

                logger.info(
                    f"found: {len(locations)} | total: {total} | progress: {progress}"
                )


if __name__ == "__main__":
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)
