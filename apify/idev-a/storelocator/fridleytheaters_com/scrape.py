from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

locator_domain = "https://www.fridleytheatres.com/"
base_url = "https://www.fridleytheatres.com/locations"


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url)
        soup = bs(res.text, "lxml")
        links = soup.select(".state-locations figure.theater-box figcaption")
        for link in links:
            page_url = urljoin(
                "https://www.fridleytheatres.com", link.select_one("a")["href"]
            )
            r1 = session.get(page_url)
            soup1 = bs(r1.text, "lxml")
            location_name = soup1.select_one("h1#theater-name").text
            _addr = " ".join([_ for _ in link.stripped_strings][1:-1])
            addr = parse_address_usa(_addr)
            _phone = [_ for _ in soup1.select_one("div#info-right").stripped_strings]
            hours_of_operation = "<MISSING>"
            msg = soup1.select("div#fxp-message img")[-1]["alt"]
            if "temporarily closed" in msg:
                hours_of_operation = "Temporarily Closed"
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country or "US",
                phone=_phone[1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
