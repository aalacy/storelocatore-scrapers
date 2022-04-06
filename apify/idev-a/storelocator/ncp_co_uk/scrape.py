from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("ncp")
locator_domain = "https://www.ncp.co.uk"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_records(http, search):
    maxZ = search.items_remaining()
    for zip in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        http.clear_cookies()
        res = http.get(
            f"https://www.ncp.co.uk/find-a-car-park/?search={zip}&address={zip}",
            headers=headers,
        ).text
        if not res:
            continue
        locations = res.split("addMarker(")[1:-1]
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logger.info(f"[{zip}] [{progress}] [{len(locations)}]")
        for loc in locations:
            _ = json.loads(
                loc.split("addMarker(")[0].split("map.fitBounds")[0].strip()[:-2]
            )
            zip_postal = _["postcodePart1"] + _["postcodePart2"]
            url = f"https://www.ncp.co.uk/find-a-car-park/car-parks/{_['urlLink']}"
            street_address = _["addressLine1"] + _["addressLine2"] + _["addressLine3"]
            hours_of_operation = _["openHours"]
            if hours_of_operation == "0":
                hours_of_operation = ""
            if hours_of_operation.endswith(";"):
                hours_of_operation = hours_of_operation[:-1]
            yield SgRecord(
                page_url=url,
                location_name=_["carParkTitle"],
                store_number=_["carParkHeadingID"],
                street_address=street_address,
                city=_["addressLine4"],
                state=_["addressLine5"],
                zip_postal=zip_postal,
                country_code="UK",
                latitude=_["latitude"],
                longitude=_["longitude"],
                phone=_["telephoneNumber"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    search = DynamicZipSearch(country_codes=[SearchableCountries.BRITAIN])
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=3
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
