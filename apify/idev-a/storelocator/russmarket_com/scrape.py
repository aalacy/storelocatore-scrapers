from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from datetime import datetime
from bs4 import BeautifulSoup as bs

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.russmarket.com",
    "referer": "https://www.russmarket.com/my-store/store-locator",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://russmarket.com/"
base_url = "https://api.freshop.com/1/stores?app_key=russ_market&has_address=true&limit=-1&token={}"
session_url = "https://api.freshop.com/2/sessions/create"


def fetch_data():
    with SgRequests() as session:
        data = {
            "app_key": "russ_market",
            "referrer": "https://www.russmarket.com/my-store/store-locator",
            "utc": datetime.utcnow(),
        }
        token = session.post(session_url, headers=_headers, data=data).json()["token"]
        locations = session.get(base_url.format(token), headers=_headers).json()[
            "items"
        ]
        for _ in locations:
            yield SgRecord(
                page_url=_["url"],
                store_number=_["store_number"],
                location_name=_["name"],
                street_address=_["address_1"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                phone=bs(_["phone"], "lxml")
                .text.strip()
                .split("Pharmacy")[0]
                .split("Fax")[0]
                .split("Floral")[0]
                .replace("Store", "")
                .replace(":", "")
                .strip(),
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=_["hours_md"]
                .split("Pharmacy")[0]
                .replace("Store:", "")
                .strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
