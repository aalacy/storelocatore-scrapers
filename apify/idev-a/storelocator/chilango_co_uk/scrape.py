from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("chilango")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://chilango.co.uk"
base_url = "https://chilango.co.uk/restaurants"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.location-list > div"
        )
        for link in locations:
            page_url = locator_domain + link.select_one("a.loc-name")["href"]
            location_type = ""
            if link.img and "temporarily-closed" in link.img["src"]:
                location_type = "temporarily closed"
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = (
                sp1.find("h3", string=re.compile(r"^Address$")).find_next_sibling().text
            )
            addr = parse_address_intl(raw_address)
            zip_postal = addr.postcode
            if not zip_postal:
                zip_postal = raw_address.split(",")[-1].strip()
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = list(
                sp1.find("h3", string=re.compile(r"^Opening Hours$"))
                .find_next_sibling()
                .stripped_strings
            )
            phone = ""
            if sp1.find("h3", string=re.compile(r"^Phone Number$")):
                phone = (
                    sp1.find("h3", string=re.compile(r"^Phone Number$"))
                    .find_next_sibling()
                    .text
                )
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code="UK",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                location_type=location_type,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
