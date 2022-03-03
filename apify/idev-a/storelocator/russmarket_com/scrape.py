from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://russmarket.com/"
    base_url = "https://api.freshop.com/1/stores?app_key=russ_market&has_address=true&limit=-1&token=4c59b22c7c370af05eb2c8d90cd6b492"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["items"]
        for _ in locations:
            yield SgRecord(
                page_url=_["url"],
                store_number=_["store_number"],
                location_name=_["name"],
                street_address=_["address_1"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                phone=_["phone"]
                .split("Pharmacy")[0]
                .split("Fax")[0]
                .split("Floral")[0]
                .replace("Store:", "")
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
