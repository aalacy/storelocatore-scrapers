from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

locator_domain = "https://www.burgerking.com.tw"
base_url = "https://www.burgerking.com.tw/storeMap"
json_url = "/AJhandler/frontierHandler.ashx"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        request = driver.wait_for_request(json_url)
        locations = json.loads(request.response.body)["args"]["branchList"]
        for _ in locations:
            yield SgRecord(
                page_url=base_url,
                store_number=_["storeid"],
                location_name=_["name"],
                street_address=_["address"].replace(_["city"], ""),
                city=_["city"],
                zip_postal=_.get("postcode"),
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Taiwan",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["todayOpenHour"].replace("~", "-"),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
