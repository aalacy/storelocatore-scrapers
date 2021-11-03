from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.cigna.com/"
    base_url = "https://www.cigna.com/static/www-cigna-com/json/contact-us-results-data.json?v=3fafd894"
    with SgRequests() as session:
        states = session.get(base_url, headers=_headers).json()["statePicker"]
        for state in states:
            for _ in state["contents"]:
                if _["header"] == "Accident, Life & Disability":
                    continue
                blocks = list(bs(_["body"], "lxml").stripped_strings)
                _addr = []
                phone = ""
                if bs(_["body"], "lxml").select_one(".tel-hidden"):
                    phone = (
                        bs(_["body"], "lxml")
                        .select_one(".tel-hidden")
                        .text.split(":")[-1]
                        .replace("Telephone", "")
                        .strip()
                    )
                    for x, block in enumerate(blocks):
                        if "Telephone" in block:
                            _addr = blocks[:x]
                            break
                else:
                    _addr = blocks[-2:]

                addr = parse_address_intl(" ".join(_addr))
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                page_url = f'https://www.cigna.com/contact-us/all-states#stateProv={state["locationName"]}'
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["header"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
