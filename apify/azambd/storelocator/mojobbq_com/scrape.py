from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
}

locator_domain = "mojobbq.com"
base_url = "https://www.mojobbq.com/locations"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("script#popmenu-apollo-state")
            .text.split("window.POPMENU_APOLLO_STATE =")[1]
            .strip()[:-1]
        )
        for key, _ in locations.items():
            if not key.startswith("RestaurantLocation:"):
                continue
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["streetAddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postalCode"],
                country_code="US",
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
