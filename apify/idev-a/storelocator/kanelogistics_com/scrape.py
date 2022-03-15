from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("kanelogistics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kanelogistics.com"
base_url = "https://www.kanelogistics.com/national-distribution"


def _d(page_url, addr, coord, phone):
    return SgRecord(
        page_url=page_url,
        location_name=addr[0],
        street_address=addr[1],
        city=addr[2].split(",")[0].strip(),
        state=addr[2].split(",")[1].strip().split(" ")[0].strip(),
        zip_postal=addr[2].split(",")[1].strip().split(" ")[-1].strip(),
        country_code="US",
        phone=phone,
        locator_domain=locator_domain,
        latitude=coord[1],
        longitude=coord[0],
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.panel-4-description p a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = ""
            _pp = sp1.find("strong", string=re.compile(r"Call us at"))
            if _pp:
                phone = _pp.text.split("at")[-1].strip()
            locations = [
                ll
                for ll in sp1.select("div.span6.widget-span.widget-type-custom_widget")
                if ll.p
            ]
            if locations:
                for _ in locations:
                    addr = list(_.select("p")[-1].stripped_strings)
                    if len(addr) == 2:
                        addr.insert(0, _.select("p")[-2].text.strip())
                    coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
                    yield _d(page_url, addr, coord, phone)
            else:
                addr = list(
                    sp1.select_one("div.map_location_div")
                    .find_previous_sibling("p")
                    .stripped_strings
                )
                if len(addr) == 2:
                    addr.insert(
                        0,
                        sp1.select_one("div.map_location_div")
                        .find_previous_sibling("p")
                        .find_previous_sibling("p")
                        .text.strip(),
                    )
                coord = (
                    _pp.find_parent()
                    .find_next_sibling("div")
                    .iframe["src"]
                    .split("!2d")[1]
                    .split("!2m")[0]
                    .split("!3d")
                )
                yield _d(page_url, addr, coord, phone)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
