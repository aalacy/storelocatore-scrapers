from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "tr",
    "content-type": "application/json",
    "origin": "https://www.endeksa.com",
    "referer": "https://www.endeksa.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://endeksa.com/tr/analiz/turkiye/malls"
base_url = "https://api.endeksa.com/ShoppingCenters"


def fetch_data():
    with SgRequests() as session:
        data = {
            "Level": 9,
            "OrderBy": 1,
            "Sort": 1,
            "ItemSize": 500,
            "ActivePageNumber": 1,
            "StoreId": [],
            "CategoryId": [],
            "ATMId": [],
        }
        locations = session.post(base_url, headers=_headers, json=data).json()["Data"]
        for _ in locations:
            page_url = f"https://www.endeksa.com/tr/malls/{'-'.join(_['Title'].lower().split())}/{_['Id']}"
            raw_address = street_address = _["Address"] or _["District"]
            addr = parse_address_intl(raw_address + ", Turkey")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                store_number=_["Id"],
                location_name=_["Title"],
                street_address=street_address,
                city=_["City"],
                state=_["County"],
                latitude=_["Lat"],
                longitude=_["Lon"],
                country_code="TR",
                phone=_["Phone"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
