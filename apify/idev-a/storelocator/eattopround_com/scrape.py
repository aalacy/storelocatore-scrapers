from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("eattopround")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://eattopround.com"
base_url = "https://eattopround.com/locations-menus"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select(
            "main a.sqs-block-button-element--small.sqs-block-button-element"
        )
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _addr = sp1.select_one("main div.sqs-block-content p")
            addr = list(_addr.stripped_strings)
            if len(addr) == 2:
                street_address = addr[0]
                city = addr[1].split(",")[0].strip()
                state = addr[1].split(",")[1].strip().split(" ")[0].strip()
                zip_postal = addr[1].split(",")[1].strip().split(" ")[-1].strip()
            else:
                addr = addr[0].replace("|", ",")
                street_address = addr.split(",")[0]
                city = addr.split(",")[1].strip()
                state = addr.split(",")[-1].strip().split(" ")[0].strip()
                zip_postal = addr.split(",")[-1].strip().split(" ")[-1].strip()

            _hr = sp1.find("", string=re.compile(r"Hours of Operation", re.IGNORECASE))
            hours = []
            if _hr:
                temp = list(_hr.find_parent("p").stripped_strings)[1:]
                for hh in _hr.find_parent("p").find_next_siblings("p"):
                    _hh = hh.text
                    if not _hh:
                        continue
                    if "phone" in _hh.lower():
                        break
                    if (
                        "Mon" in _hh
                        or "Tue" in _hh
                        or "Wed" in _hh
                        or "Thu" in _hh
                        or "Fri" in _hh
                        or "Sat" in _hh
                        or "Sun" in _hh
                    ):
                        temp += list(hh.stripped_strings)
                for hh in temp:
                    if "Hours" in hh:
                        continue
                    hours.append(hh)

            coord = (
                sp1.find("a", string=re.compile(r"GET DIRECTIONS"))["href"]
                .split("/@")[1]
                .split("/data")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=city,
                street_address=street_address.replace("\xa0", "").strip(),
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=sp1.find("a", href=re.compile(r"tel:")).text.strip(),
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
