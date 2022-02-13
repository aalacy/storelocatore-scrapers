from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://docmj.com"
base_url = "https://docmj.com"


def fetch_data():
    with SgRequests() as session:
        states = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var serviceAreasLocations =")[1]
            .split(";</script>")[0]
            .strip()
        )
        for state in states:
            for _ in state["locations"]:
                location_name = _["location_name"].replace("&#8211;", "-").strip()
                yield SgRecord(
                    page_url=base_url,
                    store_number=_["location_id"],
                    location_name=location_name,
                    city=location_name.split("(")[0]
                    .split("-")[0]
                    .replace("II", "")
                    .replace("Orlando I", "Orlando")
                    .strip(),
                    state=state["state_name"],
                    country_code="US",
                    latitude=_["coordinates"]["lat"],
                    longitude=_["coordinates"]["lng"],
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
