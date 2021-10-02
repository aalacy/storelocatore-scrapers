from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


locator_domain = "https://www.action247.com"
base_url = "https://www.action247.com/cashlocations/"
json_url = "/api/v1/maps/map_2e743d53/layers/pg_67899b52"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url)
        locations = json.loads(rr.response.body)["Children"]
        for _ in locations:
            val = _["DataSource"]["Values"]
            yield SgRecord(
                page_url=base_url,
                store_number=_["Id"].split("_")[-1],
                location_name=val[0],
                street_address=" ".join(val[:-5]),
                city=val[-5],
                state=val[-4],
                zip_postal=val[-3],
                latitude=_["LatLng"]["Lat"],
                longitude=_["LatLng"]["Lng"],
                country_code="US",
                phone=val[-2],
                locator_domain=locator_domain,
                hours_of_operation=val[-1],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
