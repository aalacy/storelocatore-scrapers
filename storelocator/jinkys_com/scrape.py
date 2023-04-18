from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.jinkys.com",
    "referer": "https://www.jinkys.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
}

locator_domain = "https://www.jinkys.com/"
base_url = "https://www.jinkys.com/graphql"

payload = {
    "operationName": "restaurantWithLocations",
    "variables": {"restaurantId": 5630},
    "extensions": {"operationId": "PopmenuClient/94a9b149c729821816fee7d97a05ecac"},
}


def fetch_data():
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers, json=payload).json()[
            "data"
        ]["restaurant"]["locations"]
        for _ in locations:
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["streetAddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postalCode"],
                country_code=_["country"] or "US",
                phone=_.get("displayPhone"),
                latitude=_.get("lat"),
                longitude=_.get("lng"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_.get("schemaHours", [])),
                raw_address=_["fullAddress"],
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
