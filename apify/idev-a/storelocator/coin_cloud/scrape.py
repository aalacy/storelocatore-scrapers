from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.coin.cloud"
base_url = "https://www.coin.cloud/dcms"


def fetch_data():
    with SgRequests() as session:
        token = bs(session.get(base_url, headers=_headers).text, "lxml").select_one(
            "div#storerocket-widget"
        )["data-storerocket-id"]
        url = f"https://api.storerocket.io/api/user/{token}/locations?lat=33.956&lng=-118.3887&radius=20"
        locations = session.get(url, headers=_headers).json()["results"]["locations"]
        for _ in locations:
            street_address = _["address_line_1"]
            if _["address_line_2"]:
                street_address += " " + _["address_line_2"]
            hours = []
            hours.append(f"Mon: {_['mon']}")
            hours.append(f"Tue: {_['tue']}")
            hours.append(f"Wed: {_['wed']}")
            hours.append(f"Thu: {_['thu']}")
            hours.append(f"Fri: {_['fri']}")
            hours.append(f"Sat: {_['sat']}")
            hours.append(f"Sun: {_['sun']}")
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_.get("postcode"),
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
