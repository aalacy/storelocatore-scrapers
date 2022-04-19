from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import bs4
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("metromattress")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://metromattress.com/"
    base_url = "https://metromattress.com/locationsmain/?per_page=500&form=2"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div#results ul.gmw-posts-wrapper li.single-post")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = _.h2.a["href"]
            logger.info(page_url)
            addr = parse_address_intl(
                " ".join(_.select_one(".address-wrapper").stripped_strings)
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = (
                _.select_one("a.gmw-get-directions")["href"]
                .split("&daddr=")[1]
                .split("&")[0]
                .split(",")
            )
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            _hr = sp1.find("h4", string=re.compile(r"HOURS"))
            temp = []
            for hh in _hr.next_siblings:
                if isinstance(hh, bs4.element.NavigableString):
                    if not hh.strip():
                        continue
                    temp.append(hh.strip())
                if isinstance(hh, bs4.element.Tag):
                    if not hh.text.strip():
                        continue
                    temp.append(hh.text.strip())
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            phone = ""
            if _.select_one("li.phone"):
                phone = _.select_one("li.phone").a.text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"].split("-")[-1],
                location_name=sp1.h1.text.strip().replace("–", "-"),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
