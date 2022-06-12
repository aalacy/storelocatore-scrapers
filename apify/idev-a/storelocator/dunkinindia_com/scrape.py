from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkinindia.com"
base_url = "https://dunkinindia.com/store-locator"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div.outlets div.row > div.columns ")
        logger.info(f"{len(links)} found")
        for link in links:
            _addr = list(link.select_one(".outlet-details p").stripped_strings)[1]
            addr = parse_address_intl(_addr)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = ""
            _hr = link.find("", string=re.compile(r"Timings"))
            if _hr:
                hours = _hr.find_parent().find_next_sibling().text.strip()
            phone = ""
            if link.find("a", href=re.compile(r"tel:")):
                phone = (
                    link.find("a", href=re.compile(r"tel:")).text.strip().split(",")[0]
                )
            if not street_address:
                street_address = _addr.split(",")[0].strip()
            yield SgRecord(
                page_url=base_url,
                location_name=link.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="India",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours.replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
