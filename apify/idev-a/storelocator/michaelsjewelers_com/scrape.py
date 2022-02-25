from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://michaelsjewelers.com/"
    base_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/6944/stores.js?callback=SMcallback2"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers).text.split("SMcallback2(")[1][:-1]
        )
        for _ in locations["stores"]:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=_["url"] or base_url,
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
