from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("royyamaguchi")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.royyamaguchi.com/"
    base_url = "https://www.royyamaguchi.com/locations"
    with SgChrome(r"/mnt/g/work/mia/old/chromedriver.exe") as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("section.Main-content div.col.sqs-col-4")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            _phone = sp1.find(
                "", string=re.compile(r"call FOR RESERVATIONS", re.IGNORECASE)
            )
            phone = ""
            if _phone:
                if _phone.find_parent("h3"):
                    phone = list(_phone.find_parent("h3").stripped_strings)[-1]
                elif _phone.find_parent("h2"):
                    phone = list(_phone.find_parent("h2").stripped_strings)[-1]

            _addr = sp1.select_one("div.sidebar__inner p")
            addr = None
            if _addr:
                _addr = list(sp1.select_one("div.sidebar__inner p").stripped_strings)
                addr = parse_address_intl(_addr[-1])
                phone = _addr[0]
            else:
                _addr = sp1.find("strong", string=re.compile(r"address", re.IGNORECASE))
                if _addr:
                    addr = parse_address_intl(
                        list(_addr.find_parent().stripped_strings)[1]
                    )
                else:
                    _addr = sp1.find_all(
                        "h3", string=re.compile(r"^Roy", re.IGNORECASE)
                    )[-1]
                    if _addr:
                        addr = parse_address_intl(_addr.text.strip())

            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _hr = sp1.find("", string=re.compile(r"DINE-IN HOURS:", re.IGNORECASE))
            hours = []
            if _hr:
                hours = list(_hr.find_parent("h3").stripped_strings)[1:]
            else:
                _hr = sp1.find("strong", string=re.compile(r"^MONDAY", re.IGNORECASE))
                if _hr:
                    temp = list(_hr.find_parent().stripped_strings)
                    for x in range(0, len(temp), 2):
                        hours.append(f"{temp[x]} {temp[x+1]}")

            yield SgRecord(
                page_url=page_url,
                location_name=link.h3.text.strip().replace("’", "'"),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
