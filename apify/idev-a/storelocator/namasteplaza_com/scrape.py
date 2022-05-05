from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.namasteplaza.com/"
base_url = "https://www.namasteplaza.com/index.php/storepickup/index/index"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var listStoreJson =")[1]
            .split(";</script>")[0]
        )
        for _ in locations:
            yield SgRecord(
                page_url=_["store_view_url"],
                store_number=_["store_id"],
                location_name=_["store_name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zipcode"],
                country_code=_["country"],
                phone=_["store_phone"],
                latitude=_["store_latitude"],
                longitude=_["store_longitude"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
