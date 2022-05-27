from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
import re
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("loscucos")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.loscucos.com/"
    base_url = "https://www.loscucos.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("main a.elementor-button-link")
        for link in locations:
            location_name = link.text.split("@")[0].strip()
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _hr = sp1.find("p", string=re.compile(r"^BUSINESS HOURS", re.IGNORECASE))
            hours = []
            if _hr:
                hours = list(
                    _hr.find_parent()
                    .find_parent()
                    .find_parent()
                    .find_next_sibling("div")
                    .stripped_strings
                )
            _addr = list(
                sp1.select_one('div[data-widget_type="heading.default"]')
                .find_next_sibling("div")
                .stripped_strings
            )
            raw_address = " ".join(_addr).replace("\n", " ").replace("\r", " ")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if sp1.find("", string=re.compile(r"^Telephone:")):
                phone = (
                    sp1.find("", string=re.compile(r"^Telephone:"))
                    .text.split(":")[-1]
                    .replace("Telephone", "")
                    .strip()
                    .split("Fax")[0]
                    .strip()
                )

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
