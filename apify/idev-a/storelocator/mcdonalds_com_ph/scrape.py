from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdelivery.com.ph"
base_url = "https://mcdelivery.com.ph/hotlines/locations"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for region in locations:
            for _ in region["branches"]:
                yield SgRecord(
                    page_url=base_url,
                    location_name=_["title"],
                    city=region["title"],
                    state=region["region"],
                    country_code="Philippines",
                    phone=_["hotlines"][0],
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.PHONE, SgRecord.Headers.CITY}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
