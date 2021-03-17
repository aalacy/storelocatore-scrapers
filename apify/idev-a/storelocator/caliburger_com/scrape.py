from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://caliburger.com"
    base_url = "https://caliburger.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.locations-block div#us-accordion")
        for _ in locations:
            try:
                prev = _.find_previous_sibling("div", class_="cali-country")
                if prev:
                    if "cali-country" in prev.get("class", []):
                        if prev.text != "United States":
                            break
                location_name = _.select_one("div.cali-store-name td").text.strip()
                if re.search(r"coming soon", location_name, re.IGNORECASE):
                    continue
                page_url = (
                    locator_domain + _.select_one("div.cali-store-name a")["href"]
                )
                addr = parse_address_intl(
                    " ".join([dd.text for dd in _.select("div.cali-store-address")])
                )
                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=addr.street_address_1,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    locator_domain=locator_domain,
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
