from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dunkin-donuts.de"
base_url = "https://dunkin-donuts-de.shop-finder.org/api/stores/search.json?callback=jQuery1102020776647745812316_1626856541580&lng=&lat=&radius=all&country_code=DE&address=&_=1626856541581"
page_url = "https://www.dunkin-donuts.de/storefinder/storefinder/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers).text.split(
                "jQuery1102020776647745812316_1626856541580("
            )[1][:-1]
        )["content"]
        for store in locations:
            _ = store["Store"]
            addr = parse_address_intl(
                " ".join(bs(_["address"], "lxml").stripped_strings)
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Germany",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(
                    bs(_["opening_hours"], "lxml").stripped_strings
                ).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
