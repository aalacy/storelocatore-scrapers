from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("sclogistics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.sclogistics.com/"
    base_url = "https://www.sclogistics.com/locations/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.marker")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = parse_address_intl(" ".join(link.p.stripped_strings))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if link.find("p", string=re.compile(r"phone", re.IGNORECASE)):
                phone = (
                    link.find("p", string=re.compile(r"phone", re.IGNORECASE))
                    .text.split(":")[-1]
                    .replace("Phone", "")
                    .strip()
                )
            yield SgRecord(
                page_url=link.a["href"],
                location_name=link.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=link["data-lat"],
                longitude=link["data-lng"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
