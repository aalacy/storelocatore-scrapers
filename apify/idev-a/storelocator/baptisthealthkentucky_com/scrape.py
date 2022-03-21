from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("baptisthealth")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.baptisthealth.com"
    base_url = "https://www.baptisthealth.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select_one("ul.dropnav-with-title").select("li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            if not page_url.startswith("http"):
                page_url = locator_domain + page_url
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = ""
            raw_address = ""
            if sp1.select_one("div.footer-address"):
                _addr = list(sp1.select_one("div.footer-address").stripped_strings)
                raw_address = " ".join(_addr[:-1])
                addr = parse_address_intl(raw_address)
                phone = _addr[-1]
            else:
                raw_address = " ".join(
                    sp1.select_one("div.contact_info p a").stripped_strings
                )
                addr = parse_address_intl(raw_address)
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _script = sp1.find_all("script", type="application/ld+json")
            latitude = longitude = ""
            hours_of_operation = ""
            if _script:
                script = json.loads(_script[-1].string.strip())
                if "geo" in script:
                    latitude = script["geo"]["latitude"]
                    longitude = script["geo"]["longitude"]
                if "openingHoursSpecification" in script:
                    day = ",".join(script["openingHoursSpecification"]["dayOfWeek"])
                    hours_of_operation = f"{day}: {script['openingHoursSpecification']['opens']}-{script['openingHoursSpecification']['closes']}"
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.title.text.split("in")[0].split("–")[-1].strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state.replace(".", ""),
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
