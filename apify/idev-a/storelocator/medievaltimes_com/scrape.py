from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def fetch_data():
    locator_domain = "https://www.medievaltimes.com"
    base_url = "https://www.medievaltimes.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#castleModal ul.castle-list li a")
        for link in locations:
            page_url = locator_domain + link["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(
                soup1.select_one("div.castle-conversion__location a").text
            )
            location_name = soup1.select_one("h1.castle-conversion__title").text
            country_code = "US"
            if addr.state in ca_provinces_codes:
                country_code = "CA"
            phone = soup1.find("a", href=re.compile(r"tel:"))["href"][4:]
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
