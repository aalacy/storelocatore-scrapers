from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("rentall")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://af-rentall.com"
base_url = "https://af-rentall.com/pages/locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("main table tr")
        for _ in locations:
            td = _.select("td")
            page_url = td[-1].a["href"]
            if not page_url.startswith("http"):
                page_url = locator_domain + page_url
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = " ".join(td[1].stripped_strings)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            _hr = sp1.find("strong", string=re.compile(r"Hours:"))
            if _hr:
                hours = list(_hr.find_parent().stripped_strings)[1:]

            yield SgRecord(
                page_url=page_url,
                location_name=td[0].text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=td[2].text.strip(),
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
