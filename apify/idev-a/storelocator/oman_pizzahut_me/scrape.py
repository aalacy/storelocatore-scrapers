from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "franchiseid": "1",
    "latitude": "",
    "longitude": "",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.oman.pizzahut.me/"
base_url = "https://www.oman.pizzahut.me/api/getallcitiesareas/parent=165"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Data"]
        for state, val in locations.items():
            for key, locs in val["areas"].items():
                for city in locs:
                    yield SgRecord(
                        location_name=city["name"],
                        city=city["name"],
                        state=state,
                        country_code="Oman",
                        locator_domain=locator_domain,
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STATE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
