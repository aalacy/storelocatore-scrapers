from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pro-duo.nl"
base_url = "https://www.pro-duo.nl/on/demandware.store/Sites-ProDuo_Trade_NL-Site/nl_NL/Stores-GetStoresJSON"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            page_url = f"https://www.pro-duo.nl/storeinfo?StoreID={_['ID']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["ID"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Netherlands",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["hours"],
                raw_address=_["formattedAddress"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
