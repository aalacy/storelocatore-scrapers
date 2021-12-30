from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.tealsmarket.com/"
base_url = "https://www.tealsmarket.com/ajax/index.php"


def fetch_data():
    with SgRequests() as session:
        data = {
            "method": "POST",
            "apiurl": "https://tealsmarket.rsaamerica.com/Services/SSWebRestApi.svc/GetClientStores/1",
        }
        locations = session.post(base_url, headers=_headers, data=data).json()[
            "GetClientStores"
        ]
        for _ in locations:
            street_address = _["AddressLine1"]
            if _["AddressLine2"] and _["StateName"] != _["AddressLine2"]:
                street_address += " " + _["AddressLine2"]
            yield SgRecord(
                page_url="https://www.tealsmarket.com/contact",
                store_number=_["StoreNumber"],
                location_name=_["ClientStoreName"],
                street_address=street_address,
                city=_["City"],
                state=_["StateName"],
                zip_postal=_["ZipCode"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="US",
                phone=_["StorePhoneNumber"],
                locator_domain=locator_domain,
                hours_of_operation=_["StoreTimings"].replace("\n", "; "),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
