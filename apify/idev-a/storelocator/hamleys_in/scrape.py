from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.hamleys.in"
base_url = "https://hmpim.hamleys.in/pim/pimresponse.php?service=storelocator&store=1"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["result"]
        for _ in locations:
            addr = parse_address_intl(_["display_address"] + ", India")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            phone = _["phone"]
            if phone == "0":
                phone = ""
            zip_postal = addr.postcode
            if zip_postal:
                zip_postal = zip_postal.split("-")[-1]
            else:
                zip_postal = _["display_address"].replace("-", " ").split()[-1]
            yield SgRecord(
                page_url="https://www.hamleys.in/storeLocator",
                store_number=_["store_id"],
                location_name=_["display_name"],
                street_address=street_address,
                city=_["city"],
                state=addr.state,
                zip_postal=zip_postal,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="India",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=_["display_address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
