from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.mclendons.com"
    base_url = "https://www.mclendons.com/Locations"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var data =")[1]
            .split("var dataFrom")[0]
            .strip()[1:-2]
        )
        for _ in locations:
            hours = bs(_["workHour"], "lxml").stripped_strings
            yield SgRecord(
                page_url=base_url,
                store_number=_["branchId"],
                location_name=_["branchName"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
