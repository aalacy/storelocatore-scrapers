from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.burgerking.com.tw"
base_url = "https://www.burgerking.com.tw/storeMap"
json_url = "https://www.burgerking.com.tw/AJhandler/frontierHandler.ashx"
payload = {
    "what": "getDeliveryInfo",
    "args": 520000,
    "list": {"type": 20, "view": 1},
    "args2": "",
}


def fetch_data():
    with SgRequests() as http:
        locations = http.post(json_url, headers=_headers, json=payload).json()["args"][
            "branchList"
        ]
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
