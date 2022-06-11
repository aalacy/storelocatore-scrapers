from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("&#39;", "'").strip()


def fetch_data():
    locator_domain = "https://bergmanluggage.com/"
    base_url = "https://bergmanluggage.com/pages/all-store-locations"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split('develic-map="')[1]
            .split('">')[0]
            .replace("&quot;", '"')
        )
        for _ in locations["items"]:
            block = list(bs(_["b"], "lxml").stripped_strings)
            addr = parse_address_intl(block[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                store_number=_["lid"],
                location_name=_valid(_["t"].split("|")[-1]),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lt"],
                longitude=_["lg"],
                country_code="US",
                phone=block[-1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
