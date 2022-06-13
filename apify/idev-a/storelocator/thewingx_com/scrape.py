from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "api.togoorder.com",
    "Origin": "https://order.thewingx.com",
    "Pragma": "no-cache",
    "Referer": "https://order.thewingx.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://thewingx.com/"
base_url = "https://api.togoorder.com/api/GetLocationMap/3380?lastMaxId={}&pageSize=5&isUnlisted=false"


def fetch_data():
    with SgRequests() as session:
        lastMaxId = 0
        while True:
            locations = session.get(base_url.format(lastMaxId), headers=_headers).json()
            if not locations:
                break
            lastMaxId = locations[-1]["Id"]
            for _ in locations:
                street_address = _["Address1"]
                if _["Address2"]:
                    street_address += " " + _["Address2"]
                hours = []
                for mo in _["OrderTypeViewModels"]:
                    if mo["OrderType"] == 2:
                        for hh in mo.get("HoursOfOperation", {}).get(
                            "WeekdayHours", []
                        ):
                            hours.append(
                                f"{hh['WeekDay']}: {hh['Start']} - {hh['Stop']}"
                            )

                yield SgRecord(
                    page_url="https://order.thewingx.com/#!/",
                    store_number=_["Id"],
                    location_name=_["LocationName"],
                    street_address=street_address,
                    city=_["City"],
                    state=_["State"],
                    zip_postal=_["Zip"],
                    latitude=_["Lat"],
                    longitude=_["Long"],
                    country_code="US",
                    phone=_["Phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
