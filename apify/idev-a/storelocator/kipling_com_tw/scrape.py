from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.com.tw"
base_url = "https://webapi.91app.com/webapi/LocationV2/GetLocationList?lat=25.037929&lon=121.548818&startIndex=0&maxCount=100&r=null&isEnableRetailStore=false&lang=zh-TW&shopId=39255"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Data"]["List"]
        for _ in locations:
            page_url = f"https://www.kipling.com.tw/Shop/StoreDetail/{_['Id']}"
            street_address = _["Address"].replace(_["CityName"], "").strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            hours = []
            hours.append(f"Weekdays: {_['NormalTime']}")
            hours.append(f"Weekends: {_['WeekendTime']}")
            location_name = "Kipling"
            if "outlet" in _["Name"].lower():
                location_name = "Kipling Outlet"
            yield SgRecord(
                page_url=page_url,
                store_number=_["Id"],
                location_name=location_name,
                street_address=street_address,
                city=_["CityName"],
                zip_postal=_["ZipCode"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="Taiwan",
                phone=_["Tel"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["Address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
