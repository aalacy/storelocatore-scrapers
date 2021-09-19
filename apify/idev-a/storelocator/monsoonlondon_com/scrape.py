from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("monsoonlondon")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.monsoonlondon.com"
base_url = "https://www.monsoonlondon.com/us/stores/?country=US"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        types = list(soup.select_one("ul.b-tabs__tabs-container").stripped_strings)
        for x in range(len(types)):
            links = soup.select("ul.b-tabs__content-container li")[x].select(
                "table tbody tr"
            )
            logger.info(f"[{types[x]}] {len(links)} found")
            for link in links:
                td = link.select("td")
                country_code = link.find_parent().find_previous_sibling().text.strip()
                addr = parse_address_intl(td[-1].text.strip())
                street_address = addr.street_address_1
                if not street_address:
                    street_address = ""
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=base_url,
                    location_name=td[1].text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=country_code,
                    location_type=types[x],
                    locator_domain=locator_domain,
                    raw_address=td[-1].text.strip(),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
