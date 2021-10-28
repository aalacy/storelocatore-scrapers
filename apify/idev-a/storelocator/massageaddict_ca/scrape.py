from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("massageaddict")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
base_url = "https://www.massageaddict.ca/locations/"
locator_domain = "https://www.massageaddict.ca"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.mobileShow.mobileProv ul a")
        logger.info(f"{len(links)} found")
        for link in links:
            url = urljoin(locator_domain, link["href"])
            locations = bs(session.get(url, headers=_headers).text, "lxml").select(
                "ul.clinicSearch li"
            )
            for _ in locations:
                raw_address = list(_.select_one(".col-sm-8").stripped_strings)[-1]
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                hours = []
                page_url = urljoin(locator_domain, _.a["href"])
                logger.info(page_url)
                res = session.get(page_url, headers=_headers)
                if res.status_code != 200:
                    continue
                sp2 = bs(res.text, "lxml")
                _hr = sp2.find("", string=re.compile(r"^Hours"))
                if _hr:
                    hours = list(
                        _hr.find_parent("p").find_next_sibling().stripped_strings
                    )

                yield SgRecord(
                    page_url=page_url,
                    location_name=sp2.h2.text.split("|")[-1].strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="CA",
                    phone=_.select_one("div.clinicSearchPhone a").text.strip(),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours)
                    .replace("\xa0", " ")
                    .replace("–", "-"),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
