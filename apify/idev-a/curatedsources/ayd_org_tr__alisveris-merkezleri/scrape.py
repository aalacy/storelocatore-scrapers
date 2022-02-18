from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://ayd.org.tr/alisveris-merkezleri"
base_url = "http://ayd.org.tr/alisveris-merkezleri"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var jsonAvms =")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            yield SgRecord(
                page_url=base_url,
                store_number=_["Id"],
                location_name=_["avmName"],
                street_address=street_address,
                city=_["city"],
                zip_postal=_["postCode"],
                latitude=_["ltd"],
                longitude=_["lng"],
                state=_["country"],
                country_code="Turkey",
                phone=_["tel1"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
