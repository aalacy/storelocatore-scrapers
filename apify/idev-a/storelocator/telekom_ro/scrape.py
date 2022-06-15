from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mobile.telekom.ro/"
base_url = "https://mobile.telekom.ro/blocks/business/magazine/magazineLocatorJson.jsp?storeCity=Bucure%C8%99ti&storeTypes=germanos&storeTypes=cosmote&storeTypes=partner"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = (
                _["address"].replace(_["city"], "").replace(_["county"], "").strip()
            )
            if street_address.endswith(","):
                street_address = street_address[:-1]
            location_type = ""
            if "orange" in _["type"]:
                location_type = "Orange Store"
            elif "cosmote" in _["type"]:
                location_type = "TKR Magazine"

            latitude = _["lat"]
            longitude = _["lng"]

            if "ERROR" in latitude:
                latitude = ""
            if "ERROR" in longitude:
                longitude = ""

            yield SgRecord(
                page_url="https://mobile.telekom.ro/magazine/",
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["county"],
                zip_postal=_["postalCode"],
                latitude=latitude,
                longitude=longitude,
                country_code="Romania",
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=_["schedule"],
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
