from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.7-eleven.dk"
base_url = "https://www.7-eleven.dk/wp-content/themes/7-eleven/get_stores_v2.php"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            if _["open"]:
                hours_of_operation = _["open"].replace(",", ";")
            else:
                hours_of_operation = "Døgnåbent "
            yield SgRecord(
                page_url=base_url,
                store_number=_["store_id"],
                location_name="7-ELEVEN",
                street_address=_["address"],
                city=_["city"],
                zip_postal=_["zipcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Denmark",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
