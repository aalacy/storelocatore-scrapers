from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", "")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    locator_domain = "https://www.corelle.com"
    base_url = "https://www.corelle.com/store-listing"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.container.rich-text-container-twig p")
        store = []
        location_name = ""
        for link in links:
            if link.text.strip():
                store.append(link.text.strip())
            if not link.text.strip():
                if not store:
                    break
                _addr = store[1:]
                if len(store) > 3:
                    location_name = store[0]
                else:
                    _addr = store
                phone = ""
                if _p(_addr[-1]):
                    phone = _addr[-1]
                    del _addr[-1]
                addr = parse_address_intl(" ".join(_addr))
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
                country_code = "US"
                if len(zip_postal) > 5:
                    country_code = "CA"
                yield SgRecord(
                    page_url=base_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    phone=phone,
                    locator_domain=locator_domain,
                )
                store = []


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
