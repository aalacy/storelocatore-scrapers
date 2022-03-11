from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.com.tw"
base_url = "https://www.carrefour.com.tw/console/api/v1/stores?page_size=all"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["data"]["rows"]
        for _ in locations:
            page_url = f"https://www.carrefour.com.tw/store-info/?store={_['name']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city_name"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="TW",
                phone=_["contact_tel"],
                location_type="store_type_name",
                locator_domain=locator_domain,
                hours_of_operation=_["en_business_hours"].replace("\n", "; "),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
