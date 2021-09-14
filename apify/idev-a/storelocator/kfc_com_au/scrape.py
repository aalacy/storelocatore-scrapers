from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

header1 = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json; charset=UTF-8",
    "referer": "https://www.kfc.com.au/find-store",
    "origin": "https://www.kfc.com.au",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kfc.com.au"
base_url = "https://www.kfc.com.au/find-store"
json_url = "https://www.kfc.com.au/KFCALocation/FindaKFCbyLatLong"


def fetch_data():
    with SgRequests(proxy_country="AU") as session:
        payload = {
            "location": {
                "SelectedOrderMode": "null",
                "DeliveryAddressInformation": "null",
                "RestaurantSearchKeyword": "null",
                "OrderReadyDateTime": "",
                "SearchedLocationGeoCode": {
                    "Latitude": "-33.8688197",
                    "Longitude": "151.2092955",
                },
                "SelectedRestaurantId": "",
                "IsCarryoutUseMyLocation": "false",
            }
        }
        _headers["__requestverificationtoken"] = bs(
            session.get(base_url, headers=header1).text, "lxml"
        ).select_one('input[name="__RequestVerificationToken"]')["value"]
        locations = json.loads(
            session.post(json_url, headers=_headers, json=payload)
            .json()["DataObject"]
            .replace('\\"', "'")
        )
        for _ in locations:
            addr = _["Address"]
            hours = []
            for day, hh in _["RestaurantTimings"].items():
                hours.append(f"{day}: {hh}")
            page_url = f"https://www.kfc.com.au/restaurants/{_['Name'].lower().replace(' ','-')}/{addr['ZipCode']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["RestaurantId"],
                location_name=_["Name"],
                street_address=addr["Street"].replace(",", ""),
                city=addr["City"],
                state=addr["State"],
                zip_postal=addr["ZipCode"],
                latitude=addr["Latitude"],
                longitude=addr["Longitude"],
                country_code="Australia",
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
