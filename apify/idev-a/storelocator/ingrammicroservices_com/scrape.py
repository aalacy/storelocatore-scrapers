from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("ingrammicroservices")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ingrammicroservices.com"
base_url = "https://www.ingrammicroservices.com/global-locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.locations-results a.location-item")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            if sp1.h1:
                location_name = sp1.h1.text.strip()
            else:
                location_name = sp1.select_one("div.banner-style1 h2").text.strip()
            addr = parse_address_intl(location_name)
            city = addr.city
            state = addr.state
            street_address = ""
            zip_postal = ""
            if sp1.find("li", string=re.compile(r"Address:")):
                addr = parse_address_intl(
                    sp1.find("li", string=re.compile(r"Address:"))
                    .text.split("Address:")[-1]
                    .strip()
                )
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                street_address = street_address
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=link.select_one(".content-country").text.strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
